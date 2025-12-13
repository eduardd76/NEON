"""
Runtime Manager for NEON
Coordinates container deployment and management
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
import logging

from app.db.models import Node, Link, Image
from app.runtime.docker import DockerRuntime
from app.runtime.network import NetworkManager

logger = logging.getLogger(__name__)


class RuntimeManager:
    """Manages network device runtime lifecycle"""

    def __init__(self):
        """Initialize runtime manager"""
        self.docker = DockerRuntime()
        self.network = NetworkManager()

    async def deploy_node(self, node: Node, image: Image, db: Session) -> Dict:
        """
        Deploy a network node

        Args:
            node: Node database model
            image: Image database model
            db: Database session

        Returns:
            Deployment result with container_id and status
        """
        try:
            logger.info(f"Deploying node {node.name} with image {image.name}")

            # Determine resource allocation
            cpu = node.cpu or image.cpu_recommended or 1
            memory = node.memory or image.memory_recommended or 512

            # Prepare environment variables
            environment = {}
            if image.default_credentials:
                environment.update({
                    "DEFAULT_USER": image.default_credentials.get("username", "admin"),
                    "DEFAULT_PASSWORD": image.default_credentials.get("password", "admin")
                })

            # Create container
            container_id = self.docker.create_container(
                image=image.image_uri,
                name=f"neon_{node.lab_id}_{node.name}",
                cpu=cpu,
                memory=memory,
                environment=environment,
                labels={
                    "neon.lab_id": str(node.lab_id),
                    "neon.node_id": str(node.id),
                    "neon.node_name": node.name
                }
            )

            # Start container
            self.docker.start_container(container_id)

            # Update node in database
            node.container_id = container_id
            node.status = "starting"
            db.commit()

            # Wait for container to be ready (non-blocking for API response)
            logger.info(f"Node {node.name} container started: {container_id[:12]}")

            return {
                "container_id": container_id,
                "status": "starting",
                "message": f"Node {node.name} deployed successfully"
            }

        except Exception as e:
            logger.error(f"Failed to deploy node {node.name}: {e}")
            node.status = "error"
            db.commit()
            raise

    async def check_node_ready(self, node: Node, image: Image, db: Session) -> bool:
        """
        Check if node is ready and update status

        Args:
            node: Node database model
            image: Image database model
            db: Database session

        Returns:
            True if ready, False otherwise
        """
        if not node.container_id:
            return False

        try:
            # Check container status
            status = self.docker.get_container_status(node.container_id)

            if status == "running":
                # Get management IP
                mgmt_ip = self.docker.get_container_ip(node.container_id)

                # Update node
                node.status = "running"
                node.mgmt_ip = mgmt_ip
                db.commit()

                logger.info(f"Node {node.name} is ready (IP: {mgmt_ip})")
                return True

            elif status in ["exited", "not_found"]:
                node.status = "error"
                db.commit()
                logger.error(f"Node {node.name} failed to start")
                return False

            return False

        except Exception as e:
            logger.error(f"Error checking node {node.name} status: {e}")
            return False

    async def stop_node(self, node: Node, db: Session) -> Dict:
        """Stop a running node"""
        try:
            if not node.container_id:
                return {"status": "not_deployed", "message": "Node has no container"}

            self.docker.stop_container(node.container_id)

            node.status = "stopped"
            db.commit()

            return {
                "status": "stopped",
                "message": f"Node {node.name} stopped successfully"
            }

        except Exception as e:
            logger.error(f"Failed to stop node {node.name}: {e}")
            raise

    async def destroy_node(self, node: Node, db: Session) -> Dict:
        """Destroy a node and remove its container"""
        try:
            if not node.container_id:
                return {"status": "not_deployed", "message": "Node has no container"}

            self.docker.remove_container(node.container_id)

            node.container_id = None
            node.status = "stopped"
            node.mgmt_ip = None
            db.commit()

            return {
                "status": "destroyed",
                "message": f"Node {node.name} destroyed successfully"
            }

        except Exception as e:
            logger.error(f"Failed to destroy node {node.name}: {e}")
            raise

    async def create_link(self, link: Link, db: Session) -> Dict:
        """
        Create a network link between two nodes using veth pairs
        """
        try:
            logger.info(
                f"Creating link: {link.source_node.name}:{link.source_interface} "
                f"<-> {link.target_node.name}:{link.target_interface}"
            )

            # Get container IDs from nodes
            source_node = link.source_node
            target_node = link.target_node

            if not source_node.container_id or not target_node.container_id:
                return {
                    "status": "error",
                    "message": "Both nodes must be deployed before creating links"
                }

            # Create veth pair link
            success = self.network.create_veth_link(
                container_a_id=source_node.container_id,
                container_a_iface=link.source_interface,
                container_b_id=target_node.container_id,
                container_b_iface=link.target_interface,
                bandwidth=link.bandwidth,
                delay_ms=link.delay_ms,
                loss_percent=float(link.loss_percent) if link.loss_percent else None
            )

            if success:
                link.status = "up"
                db.commit()

                return {
                    "status": "created",
                    "message": "Link created successfully with veth pair"
                }
            else:
                link.status = "error"
                db.commit()

                return {
                    "status": "error",
                    "message": "Failed to create veth link"
                }

        except Exception as e:
            logger.error(f"Failed to create link: {e}")
            link.status = "error"
            db.commit()
            raise

    async def destroy_link(self, link: Link, db: Session) -> Dict:
        """
        Destroy a network link between nodes
        """
        try:
            logger.info(
                f"Destroying link: {link.source_node.name}:{link.source_interface} "
                f"<-> {link.target_node.name}:{link.target_interface}"
            )

            source_node = link.source_node
            target_node = link.target_node

            if not source_node.container_id or not target_node.container_id:
                return {
                    "status": "not_deployed",
                    "message": "Nodes are not deployed"
                }

            # Delete veth link
            success = self.network.delete_link(
                container_a_id=source_node.container_id,
                container_a_iface=link.source_interface,
                container_b_id=target_node.container_id,
                container_b_iface=link.target_interface
            )

            if success:
                link.status = "down"
                db.commit()

                return {
                    "status": "destroyed",
                    "message": "Link destroyed successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to destroy link"
                }

        except Exception as e:
            logger.error(f"Failed to destroy link: {e}")
            raise

    def get_runtime_stats(self) -> Dict:
        """Get runtime statistics"""
        try:
            containers = self.docker.list_neon_containers()

            return {
                "total_containers": len(containers),
                "running": sum(1 for c in containers if c["status"] == "running"),
                "stopped": sum(1 for c in containers if c["status"] != "running"),
                "containers": containers
            }

        except Exception as e:
            logger.error(f"Failed to get runtime stats: {e}")
            return {"error": str(e)}


# Singleton instance (lazy initialization)
_runtime_manager = None


def get_runtime() -> RuntimeManager:
    """Dependency injection for FastAPI with lazy initialization"""
    global _runtime_manager
    if _runtime_manager is None:
        _runtime_manager = RuntimeManager()
    return _runtime_manager
