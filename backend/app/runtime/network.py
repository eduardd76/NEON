"""
Network Link Management for NEON
Handles veth pairs and network connections between containers
"""
import subprocess
import logging
from typing import Optional
import docker
from docker.errors import DockerException, NotFound

logger = logging.getLogger(__name__)


class NetworkManager:
    """Manages network links between containers"""

    def __init__(self):
        """Initialize network manager"""
        self.client = docker.from_env()

    def create_veth_link(
        self,
        container_a_id: str,
        container_a_iface: str,
        container_b_id: str,
        container_b_iface: str,
        bandwidth: Optional[str] = None,
        delay_ms: Optional[int] = None,
        loss_percent: Optional[float] = None
    ) -> bool:
        """
        Create a veth pair link between two containers

        Args:
            container_a_id: First container ID
            container_a_iface: Interface name in first container (e.g., 'eth1')
            container_b_id: Second container ID
            container_b_iface: Interface name in second container (e.g., 'eth1')
            bandwidth: Bandwidth limit (e.g., '1gbit', '100mbit')
            delay_ms: Network delay in milliseconds
            loss_percent: Packet loss percentage

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get container PIDs for namespace manipulation
            container_a = self.client.containers.get(container_a_id)
            container_b = self.client.containers.get(container_b_id)

            pid_a = container_a.attrs['State']['Pid']
            pid_b = container_b.attrs['State']['Pid']

            # Generate veth pair names (unique to avoid conflicts)
            veth_a = f"veth{pid_a}_{container_a_iface.replace('/', '_')}"
            veth_b = f"veth{pid_b}_{container_b_iface.replace('/', '_')}"

            # Truncate to 15 chars (Linux interface name limit)
            veth_a = veth_a[:15]
            veth_b = veth_b[:15]

            logger.info(f"Creating veth pair: {veth_a} <-> {veth_b}")

            # Create veth pair in host namespace
            subprocess.run(
                ["ip", "link", "add", veth_a, "type", "veth", "peer", "name", veth_b],
                check=True,
                capture_output=True
            )

            # Move veth_a into container A's namespace
            subprocess.run(
                ["ip", "link", "set", veth_a, "netns", str(pid_a)],
                check=True,
                capture_output=True
            )

            # Move veth_b into container B's namespace
            subprocess.run(
                ["ip", "link", "set", veth_b, "netns", str(pid_b)],
                check=True,
                capture_output=True
            )

            # Rename interfaces inside containers and bring them up
            # Container A
            subprocess.run(
                ["nsenter", "-t", str(pid_a), "-n", "ip", "link", "set", veth_a, "name", container_a_iface],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["nsenter", "-t", str(pid_a), "-n", "ip", "link", "set", container_a_iface, "up"],
                check=True,
                capture_output=True
            )

            # Container B
            subprocess.run(
                ["nsenter", "-t", str(pid_b), "-n", "ip", "link", "set", veth_b, "name", container_b_iface],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["nsenter", "-t", str(pid_b), "-n", "ip", "link", "set", container_b_iface, "up"],
                check=True,
                capture_output=True
            )

            # Apply traffic control if specified
            if bandwidth or delay_ms or loss_percent:
                self._apply_tc(pid_a, container_a_iface, bandwidth, delay_ms, loss_percent)
                self._apply_tc(pid_b, container_b_iface, bandwidth, delay_ms, loss_percent)

            logger.info(f"Successfully created link: {container_a_id[:12]}:{container_a_iface} <-> {container_b_id[:12]}:{container_b_iface}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create veth link: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except DockerException as e:
            logger.error(f"Docker error creating link: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating link: {e}")
            return False

    def _apply_tc(
        self,
        pid: int,
        interface: str,
        bandwidth: Optional[str] = None,
        delay_ms: Optional[int] = None,
        loss_percent: Optional[float] = None
    ) -> None:
        """
        Apply traffic control (tc) to interface for network impairment

        Args:
            pid: Container PID
            interface: Interface name
            bandwidth: Bandwidth limit (e.g., '1gbit')
            delay_ms: Network delay in milliseconds
            loss_percent: Packet loss percentage
        """
        try:
            # Build tc command for netem
            tc_params = []

            if delay_ms:
                tc_params.extend(["delay", f"{delay_ms}ms"])

            if loss_percent:
                tc_params.extend(["loss", f"{loss_percent}%"])

            if tc_params:
                # Add qdisc for netem
                cmd = ["nsenter", "-t", str(pid), "-n", "tc", "qdisc", "add", "dev", interface, "root", "netem"] + tc_params
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Applied tc netem to {interface}: {' '.join(tc_params)}")

            if bandwidth:
                # Add tbf (token bucket filter) for bandwidth limiting
                # This is a simplified version - production would need more sophisticated qdisc setup
                cmd = [
                    "nsenter", "-t", str(pid), "-n",
                    "tc", "qdisc", "add", "dev", interface, "root", "tbf",
                    "rate", bandwidth,
                    "burst", "32kbit",
                    "latency", "50ms"
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Applied tc tbf to {interface}: rate {bandwidth}")

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to apply tc: {e.stderr.decode() if e.stderr else str(e)}")

    def delete_link(
        self,
        container_a_id: str,
        container_a_iface: str,
        container_b_id: str,
        container_b_iface: str
    ) -> bool:
        """
        Delete a veth link between containers

        Args:
            container_a_id: First container ID
            container_a_iface: Interface name in first container
            container_b_id: Second container ID
            container_b_iface: Interface name in second container

        Returns:
            True if successful, False otherwise
        """
        try:
            container_a = self.client.containers.get(container_a_id)
            pid_a = container_a.attrs['State']['Pid']

            # Deleting one end of veth pair automatically deletes the other
            subprocess.run(
                ["nsenter", "-t", str(pid_a), "-n", "ip", "link", "delete", container_a_iface],
                check=True,
                capture_output=True
            )

            logger.info(f"Deleted link: {container_a_id[:12]}:{container_a_iface} <-> {container_b_id[:12]}:{container_b_iface}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete link: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except DockerException as e:
            logger.error(f"Docker error deleting link: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting link: {e}")
            return False

    def list_interfaces(self, container_id: str) -> list[str]:
        """
        List all network interfaces in a container

        Args:
            container_id: Container ID

        Returns:
            List of interface names
        """
        try:
            container = self.client.containers.get(container_id)
            pid = container.attrs['State']['Pid']

            result = subprocess.run(
                ["nsenter", "-t", str(pid), "-n", "ip", "-o", "link", "show"],
                check=True,
                capture_output=True,
                text=True
            )

            interfaces = []
            for line in result.stdout.strip().split('\n'):
                # Parse "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> ..."
                parts = line.split(':')
                if len(parts) >= 2:
                    iface = parts[1].strip()
                    # Skip loopback
                    if iface != 'lo':
                        interfaces.append(iface)

            return interfaces

        except (subprocess.CalledProcessError, DockerException) as e:
            logger.error(f"Failed to list interfaces: {e}")
            return []
