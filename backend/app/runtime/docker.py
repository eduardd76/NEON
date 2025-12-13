"""
Docker Runtime Manager for NEON
Handles container lifecycle for network devices
"""
import docker
from docker.errors import DockerException, NotFound
from typing import Dict, List, Optional
import logging
import time

logger = logging.getLogger(__name__)


class DockerRuntime:
    """Manages Docker containers for network emulation"""

    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("Docker client initialized successfully")
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

    def create_container(
        self,
        image: str,
        name: str,
        cpu: Optional[int] = None,
        memory: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
        network_mode: str = "bridge",
        privileged: bool = True,
        **kwargs
    ) -> str:
        """
        Create a Docker container for a network device

        Args:
            image: Docker image URI (e.g., 'ghcr.io/nokia/srlinux:latest')
            name: Container name
            cpu: CPU count (optional, uses image default if not specified)
            memory: Memory in MB (optional, uses image default if not specified)
            environment: Environment variables
            network_mode: Docker network mode
            privileged: Run in privileged mode (required for network devices)
            **kwargs: Additional Docker container arguments

        Returns:
            Container ID
        """
        try:
            # Pull image if not available
            try:
                self.client.images.get(image)
                logger.info(f"Using existing image: {image}")
            except NotFound:
                logger.info(f"Pulling image: {image}")
                self.client.images.pull(image)

            # Prepare container configuration
            container_config = {
                "image": image,
                "name": name,
                "detach": True,
                "network_mode": network_mode,
                "privileged": privileged,
                "environment": environment or {},
                "labels": {
                    "neon.managed": "true",
                    "neon.type": "network-device"
                }
            }

            # Add resource limits if specified
            if cpu or memory:
                container_config["nano_cpus"] = int((cpu or 1) * 1e9)
                container_config["mem_limit"] = f"{memory or 512}m"

            # Create container
            container = self.client.containers.create(**container_config, **kwargs)
            logger.info(f"Created container {name} ({container.id[:12]})")

            return container.id

        except DockerException as e:
            logger.error(f"Failed to create container {name}: {e}")
            raise

    def start_container(self, container_id: str) -> None:
        """Start a container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"Started container {container_id[:12]}")
        except DockerException as e:
            logger.error(f"Failed to start container {container_id[:12]}: {e}")
            raise

    def stop_container(self, container_id: str, timeout: int = 10) -> None:
        """Stop a container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            logger.info(f"Stopped container {container_id[:12]}")
        except DockerException as e:
            logger.error(f"Failed to stop container {container_id[:12]}: {e}")
            raise

    def remove_container(self, container_id: str, force: bool = True) -> None:
        """Remove a container"""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            logger.info(f"Removed container {container_id[:12]}")
        except DockerException as e:
            logger.error(f"Failed to remove container {container_id[:12]}: {e}")
            raise

    def get_container_status(self, container_id: str) -> str:
        """
        Get container status

        Returns:
            Status string: 'running', 'exited', 'created', 'restarting', 'paused'
        """
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except NotFound:
            return "not_found"
        except DockerException as e:
            logger.error(f"Failed to get status for {container_id[:12]}: {e}")
            raise

    def get_container_ip(self, container_id: str, network: str = "bridge") -> Optional[str]:
        """Get container IP address"""
        try:
            container = self.client.containers.get(container_id)
            container.reload()  # Refresh container info

            networks = container.attrs.get("NetworkSettings", {}).get("Networks", {})
            if network in networks:
                return networks[network].get("IPAddress")

            # Fallback to first available network
            for net_name, net_info in networks.items():
                if ip := net_info.get("IPAddress"):
                    return ip

            return None

        except DockerException as e:
            logger.error(f"Failed to get IP for {container_id[:12]}: {e}")
            return None

    def wait_for_ready(
        self,
        container_id: str,
        timeout: int = 300,
        check_interval: int = 5
    ) -> bool:
        """
        Wait for container to be ready

        Args:
            container_id: Container ID
            timeout: Maximum wait time in seconds
            check_interval: Time between checks in seconds

        Returns:
            True if container is ready, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_container_status(container_id)

            if status == "running":
                # Container is running, give it a bit more time to initialize
                time.sleep(check_interval)
                return True

            if status in ["exited", "not_found"]:
                logger.error(f"Container {container_id[:12]} failed to start")
                return False

            time.sleep(check_interval)

        logger.warning(f"Container {container_id[:12]} did not become ready within {timeout}s")
        return False

    def create_network(self, name: str, driver: str = "bridge") -> str:
        """Create a Docker network for lab isolation"""
        try:
            network = self.client.networks.create(
                name=name,
                driver=driver,
                labels={"neon.managed": "true"}
            )
            logger.info(f"Created network {name} ({network.id[:12]})")
            return network.id
        except DockerException as e:
            logger.error(f"Failed to create network {name}: {e}")
            raise

    def connect_to_network(self, container_id: str, network_id: str) -> None:
        """Connect container to a network"""
        try:
            network = self.client.networks.get(network_id)
            network.connect(container_id)
            logger.info(f"Connected {container_id[:12]} to network {network_id[:12]}")
        except DockerException as e:
            logger.error(f"Failed to connect container to network: {e}")
            raise

    def list_neon_containers(self) -> List[Dict]:
        """List all NEON-managed containers"""
        try:
            containers = self.client.containers.list(
                all=True,
                filters={"label": "neon.managed=true"}
            )

            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else c.image.id
                }
                for c in containers
            ]
        except DockerException as e:
            logger.error(f"Failed to list containers: {e}")
            return []

    def cleanup_lab(self, lab_id: str) -> None:
        """Remove all containers for a specific lab"""
        try:
            containers = self.client.containers.list(
                all=True,
                filters={"label": f"neon.lab_id={lab_id}"}
            )

            for container in containers:
                try:
                    container.remove(force=True)
                    logger.info(f"Removed container {container.name}")
                except DockerException as e:
                    logger.error(f"Failed to remove {container.name}: {e}")

        except DockerException as e:
            logger.error(f"Failed to cleanup lab {lab_id}: {e}")
