"""
WebSocket endpoint for device console access
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import asyncio
import docker
from docker.errors import DockerException, NotFound

from app.db.session import get_db
from app.db.models import Node

router = APIRouter()


@router.websocket("/nodes/{node_id}/console")
async def console_websocket(websocket: WebSocket, node_id: UUID, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for console access to a node

    Establishes a bidirectional connection between the web terminal and the container
    """
    await websocket.accept()

    try:
        # Get node from database
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            await websocket.send_json({"error": "Node not found"})
            await websocket.close(code=1008)
            return

        if not node.container_id:
            await websocket.send_json({"error": "Node not deployed"})
            await websocket.close(code=1008)
            return

        # Connect to Docker
        client = docker.from_env()

        try:
            container = client.containers.get(node.container_id)
        except NotFound:
            await websocket.send_json({"error": "Container not found"})
            await websocket.close(code=1008)
            return

        # Create exec instance for interactive shell
        # Use bash for Linux containers, or appropriate shell for network devices
        shell_cmd = ["/bin/bash"] if node.image.type == "host" else ["/bin/sh"]

        exec_instance = client.api.exec_create(
            container.id,
            shell_cmd,
            stdin=True,
            tty=True,
            environment={"TERM": "xterm-256color"}
        )

        exec_socket = client.api.exec_start(
            exec_instance['Id'],
            socket=True,
            tty=True
        )

        # Task to read from container and send to WebSocket
        async def container_to_websocket():
            try:
                while True:
                    # Read from container socket
                    chunk = exec_socket._sock.recv(4096)
                    if not chunk:
                        break

                    # Send to WebSocket
                    await websocket.send_text(chunk.decode('utf-8', errors='replace'))

            except Exception as e:
                print(f"Error reading from container: {e}")
            finally:
                await websocket.close()

        # Task to read from WebSocket and send to container
        async def websocket_to_container():
            try:
                while True:
                    # Read from WebSocket
                    data = await websocket.receive_text()

                    # Send to container
                    exec_socket._sock.send(data.encode('utf-8'))

            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"Error sending to container: {e}")

        # Run both tasks concurrently
        await asyncio.gather(
            container_to_websocket(),
            websocket_to_container()
        )

    except DockerException as e:
        await websocket.send_json({"error": f"Docker error: {str(e)}"})
        await websocket.close(code=1011)

    except Exception as e:
        print(f"Console WebSocket error: {e}")
        await websocket.close(code=1011)

    finally:
        # Cleanup
        if 'exec_socket' in locals():
            exec_socket.close()
        if 'client' in locals():
            client.close()
