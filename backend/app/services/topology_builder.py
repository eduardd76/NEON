"""
Topology Builder Service
Builds network topologies from AI-generated actions
"""
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session
import logging
import math

from app.db.models import Lab, Node, Link, Image

logger = logging.getLogger(__name__)


class TopologyBuilder:
    """Service for building topologies from structured AI actions"""

    def add_nodes(self, lab_id: UUID, nodes: List[Dict], db: Session) -> List[Dict]:
        """
        Add multiple nodes to a lab

        Args:
            lab_id: Lab UUID
            nodes: List of node specifications
                [{
                    "name": "R1",
                    "type": "router",
                    "image": "ceos",  # image name
                    "vendor": "arista",  # optional
                    "position": {"x": 100, "y": 100}  # optional
                }]
            db: Database session

        Returns:
            List of created node summaries
        """
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            raise ValueError(f"Lab {lab_id} not found")

        created_nodes = []
        existing_count = len(lab.nodes)

        # Calculate positions if not provided
        positions = self._calculate_grid_positions(len(nodes), existing_count)

        for idx, node_spec in enumerate(nodes):
            # Find image
            image_query = db.query(Image).filter(Image.is_active == True)

            # Match by name
            if "image" in node_spec:
                image_query = image_query.filter(Image.name.ilike(f"%{node_spec['image']}%"))

            # Match by type
            if "type" in node_spec:
                image_query = image_query.filter(Image.type == node_spec["type"])

            # Match by vendor (use has() correlated subquery; no explicit join needed)
            if "vendor" in node_spec:
                image_query = image_query.filter(
                    Image.vendor.has(name=node_spec["vendor"])
                )

            image = image_query.first()
            if not image:
                logger.warning(f"No image found for spec: {node_spec}")
                # Try fallback to first image of type
                image = db.query(Image).filter(
                    Image.type == node_spec.get("type", "router"),
                    Image.is_active == True
                ).first()

            if not image:
                raise ValueError(f"Cannot find suitable image for node {node_spec.get('name')}")

            # Get position
            position = node_spec.get("position", positions[idx])

            # Create node
            node = Node(
                lab_id=lab_id,
                image_id=image.id,
                name=node_spec.get("name", f"{image.name}{existing_count + idx + 1}"),
                hostname=node_spec.get("hostname"),
                position_x=position.get("x", 100),
                position_y=position.get("y", 100),
                cpu=node_spec.get("cpu"),
                memory=node_spec.get("memory"),
                status="stopped"
            )

            db.add(node)
            db.flush()  # Get node ID

            created_nodes.append({
                "id": str(node.id),
                "name": node.name,
                "type": image.type,
                "image": image.name,
                "position": {"x": node.position_x, "y": node.position_y}
            })

            logger.info(f"Created node {node.name} with image {image.name}")

        db.commit()
        return created_nodes

    def add_links(self, lab_id: UUID, links: List[Dict], db: Session) -> List[Dict]:
        """
        Add multiple links between nodes

        Args:
            lab_id: Lab UUID
            links: List of link specifications
                [{
                    "source": "R1",  # node name
                    "source_interface": "eth1",
                    "target": "R2",
                    "target_interface": "eth1",
                    "properties": {  # optional
                        "bandwidth": "1gbit",
                        "delay_ms": 10,
                        "loss_percent": 0.1
                    }
                }]
            db: Database session

        Returns:
            List of created link summaries
        """
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            raise ValueError(f"Lab {lab_id} not found")

        created_links = []

        # Build node name to ID map
        nodes_by_name = {node.name: node for node in lab.nodes}

        # Seed used-interface tracking from links already persisted in the DB.
        # We maintain this dict ourselves so that interfaces assigned within
        # this batch are visible to subsequent iterations (lab.links is a
        # SQLAlchemy lazy collection that is NOT refreshed after each flush).
        used_interfaces: Dict[str, set] = {}
        for existing_link in lab.links:
            src_id = str(existing_link.source_node_id)
            tgt_id = str(existing_link.target_node_id)
            used_interfaces.setdefault(src_id, set()).add(existing_link.source_interface)
            used_interfaces.setdefault(tgt_id, set()).add(existing_link.target_interface)

        def _next_iface(node_id: str, prefix: str = "eth") -> str:
            used = used_interfaces.get(str(node_id), set())
            i = 0
            while f"{prefix}{i}" in used:
                i += 1
            return f"{prefix}{i}"

        for link_spec in links:
            source_name = link_spec["source"]
            target_name = link_spec["target"]

            source_node = nodes_by_name.get(source_name)
            target_node = nodes_by_name.get(target_name)

            if not source_node:
                raise ValueError(f"Source node '{source_name}' not found in lab")
            if not target_node:
                raise ValueError(f"Target node '{target_name}' not found in lab")

            # Auto-assign interfaces if not provided
            source_iface = link_spec.get("source_interface")
            target_iface = link_spec.get("target_interface")

            if not source_iface:
                source_iface = _next_iface(source_node.id)
            if not target_iface:
                target_iface = _next_iface(target_node.id)

            # Record assignment so next iteration sees these interfaces as used
            used_interfaces.setdefault(str(source_node.id), set()).add(source_iface)
            used_interfaces.setdefault(str(target_node.id), set()).add(target_iface)

            # Get properties
            props = link_spec.get("properties", {})

            # Create link
            link = Link(
                lab_id=lab_id,
                source_node_id=source_node.id,
                source_interface=source_iface,
                target_node_id=target_node.id,
                target_interface=target_iface,
                bandwidth=props.get("bandwidth"),
                delay_ms=props.get("delay_ms", 0),
                loss_percent=props.get("loss_percent", 0.0),
                jitter_ms=props.get("jitter_ms", 0),
                status="down"
            )

            db.add(link)
            db.flush()

            created_links.append({
                "id": str(link.id),
                "source": f"{source_name}:{source_iface}",
                "target": f"{target_name}:{target_iface}",
                "properties": props
            })

            logger.info(f"Created link: {source_name}:{source_iface} <-> {target_name}:{target_iface}")

        db.commit()
        return created_links

    def create_topology_pattern(
        self,
        lab_id: UUID,
        pattern: str,
        count: Union[int, Dict],
        image_type: str,
        db: Session
    ) -> Dict:
        """
        Create a topology using a predefined pattern

        Supported patterns:
        - "ring": Devices connected in a ring
        - "mesh": Full mesh connectivity
        - "star": Star topology with central device
        - "spine-leaf": Spine-leaf datacenter topology

        Args:
            lab_id: Lab UUID
            pattern: Topology pattern name
            count: Number of devices (or dict with spine/leaf counts)
            image_type: Type of image to use
            db: Database session

        Returns:
            Summary of created topology
        """
        if pattern == "ring":
            if not isinstance(count, int):
                raise ValueError("ring pattern requires an integer count")
            return self._create_ring(lab_id, count, image_type, db)
        elif pattern == "mesh":
            if not isinstance(count, int):
                raise ValueError("mesh pattern requires an integer count")
            return self._create_mesh(lab_id, count, image_type, db)
        elif pattern == "star":
            if not isinstance(count, int):
                raise ValueError("star pattern requires an integer count")
            return self._create_star(lab_id, count, image_type, db)
        elif pattern == "spine-leaf":
            if not isinstance(count, dict):
                raise ValueError("spine-leaf pattern requires a dict with 'spines' and 'leaves' keys")
            return self._create_spine_leaf(lab_id, count, image_type, db)
        else:
            raise ValueError(f"Unknown topology pattern: {pattern}")

    def _create_ring(self, lab_id: UUID, count: int, image_type: str, db: Session) -> Dict:
        """Create a ring topology"""
        # Create nodes
        nodes = []
        for i in range(count):
            nodes.append({
                "name": f"R{i+1}",
                "type": image_type
            })

        created_nodes = self.add_nodes(lab_id, nodes, db)

        # Create links in a ring
        links = []
        for i in range(count):
            next_i = (i + 1) % count
            links.append({
                "source": f"R{i+1}",
                "target": f"R{next_i+1}"
            })

        created_links = self.add_links(lab_id, links, db)

        return {
            "pattern": "ring",
            "nodes": created_nodes,
            "links": created_links
        }

    def _create_mesh(self, lab_id: UUID, count: int, image_type: str, db: Session) -> Dict:
        """Create a full mesh topology"""
        # Create nodes
        nodes = [{"name": f"R{i+1}", "type": image_type} for i in range(count)]
        created_nodes = self.add_nodes(lab_id, nodes, db)

        # Create full mesh links
        links = []
        for i in range(count):
            for j in range(i + 1, count):
                links.append({
                    "source": f"R{i+1}",
                    "target": f"R{j+1}"
                })

        created_links = self.add_links(lab_id, links, db)

        return {
            "pattern": "mesh",
            "nodes": created_nodes,
            "links": created_links
        }

    def _create_star(self, lab_id: UUID, count: int, image_type: str, db: Session) -> Dict:
        """Create a star topology"""
        # Create central node
        nodes = [{"name": "Core", "type": image_type}]

        # Create spoke nodes
        for i in range(count - 1):
            nodes.append({"name": f"Edge{i+1}", "type": image_type})

        created_nodes = self.add_nodes(lab_id, nodes, db)

        # Create links from core to all edges
        links = []
        for i in range(count - 1):
            links.append({
                "source": "Core",
                "target": f"Edge{i+1}"
            })

        created_links = self.add_links(lab_id, links, db)

        return {
            "pattern": "star",
            "nodes": created_nodes,
            "links": created_links
        }

    def _create_spine_leaf(self, lab_id: UUID, counts: Dict, image_type: str, db: Session) -> Dict:
        """Create a spine-leaf topology"""
        spine_count = counts.get("spines", 2)
        leaf_count = counts.get("leaves", 4)

        # Create spine nodes
        nodes = []
        for i in range(spine_count):
            nodes.append({"name": f"Spine{i+1}", "type": "switch"})

        # Create leaf nodes
        for i in range(leaf_count):
            nodes.append({"name": f"Leaf{i+1}", "type": "switch"})

        created_nodes = self.add_nodes(lab_id, nodes, db)

        # Create links: every leaf connects to every spine
        links = []
        for spine_i in range(spine_count):
            for leaf_i in range(leaf_count):
                links.append({
                    "source": f"Spine{spine_i+1}",
                    "target": f"Leaf{leaf_i+1}"
                })

        created_links = self.add_links(lab_id, links, db)

        return {
            "pattern": "spine-leaf",
            "nodes": created_nodes,
            "links": created_links
        }

    def _calculate_grid_positions(self, count: int, offset: int = 0) -> List[Dict]:
        """Calculate grid positions for nodes"""
        positions = []
        cols = math.ceil(math.sqrt(count))

        spacing_x = 200
        spacing_y = 150
        start_x = 100
        start_y = 100

        for i in range(count):
            row = i // cols
            col = i % cols

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y + (offset // cols) * spacing_y

            positions.append({"x": x, "y": y})

        return positions

    def _auto_assign_interfaces(
        self,
        node_a: Node,
        node_b: Node,
        existing_links: List[Link]
    ) -> Tuple[str, str]:
        """
        Auto-assign interface names for a link

        Returns:
            Tuple of (interface_a, interface_b)
        """
        # Count existing interfaces for each node
        used_interfaces_a = set()
        used_interfaces_b = set()

        for link in existing_links:
            if link.source_node_id == node_a.id:
                used_interfaces_a.add(link.source_interface)
            if link.target_node_id == node_a.id:
                used_interfaces_a.add(link.target_interface)

            if link.source_node_id == node_b.id:
                used_interfaces_b.add(link.source_interface)
            if link.target_node_id == node_b.id:
                used_interfaces_b.add(link.target_interface)

        # Find next available interface
        def next_interface(used: set, prefix: str = "eth") -> str:
            i = 0
            while f"{prefix}{i}" in used:
                i += 1
            return f"{prefix}{i}"

        return (
            next_interface(used_interfaces_a),
            next_interface(used_interfaces_b)
        )
