"""
Labs API endpoints
Manage network topology labs
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.db.base import get_db
from app.db.models import Lab, Node, Link, Image
from app.runtime.manager import get_runtime, RuntimeManager
from datetime import datetime

router = APIRouter()


class LabCreate(BaseModel):
    name: str
    description: Optional[str] = None


class NodeCreate(BaseModel):
    image_id: UUID
    name: str
    position_x: int = 100
    position_y: int = 100
    cpu: Optional[int] = None
    memory: Optional[int] = None


class LinkCreate(BaseModel):
    source_node_id: UUID
    source_interface: str
    target_node_id: UUID
    target_interface: str


@router.get("/")
async def list_labs(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all labs with optional status filter
    """
    query = db.query(Lab)

    if status:
        query = query.filter(Lab.status == status)

    labs = query.all()

    return {
        "count": len(labs),
        "labs": [
            {
                "id": str(lab.id),
                "name": lab.name,
                "description": lab.description,
                "status": lab.status,
                "node_count": len(lab.nodes),
                "link_count": len(lab.links),
                "created_at": lab.created_at.isoformat() if lab.created_at else None,
                "updated_at": lab.updated_at.isoformat() if lab.updated_at else None,
                "deployed_at": lab.deployed_at.isoformat() if lab.deployed_at else None
            }
            for lab in labs
        ]
    }


@router.post("/")
async def create_lab(
    lab: LabCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lab
    """
    db_lab = Lab(
        name=lab.name,
        description=lab.description,
        status="draft"
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)

    return {
        "id": str(db_lab.id),
        "name": db_lab.name,
        "description": db_lab.description,
        "status": db_lab.status,
        "created_at": db_lab.created_at.isoformat() if db_lab.created_at else None
    }


@router.get("/{lab_id}")
async def get_lab(lab_id: UUID, db: Session = Depends(get_db)):
    """
    Get detailed lab information including nodes and links
    """
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    return {
        "id": str(lab.id),
        "name": lab.name,
        "description": lab.description,
        "status": lab.status,
        "nodes": [
            {
                "id": str(node.id),
                "name": node.name,
                "hostname": node.hostname,
                "image": {
                    "id": str(node.image.id),
                    "name": node.image.name,
                    "display_name": node.image.display_name,
                    "type": node.image.type
                } if node.image else None,
                "position": {
                    "x": node.position_x,
                    "y": node.position_y
                },
                "resources": {
                    "cpu": node.cpu,
                    "memory": node.memory
                },
                "status": node.status,
                "mgmt_ip": str(node.mgmt_ip) if node.mgmt_ip else None,
                "console_port": node.console_port
            }
            for node in lab.nodes
        ],
        "links": [
            {
                "id": str(link.id),
                "source": {
                    "node_id": str(link.source_node_id),
                    "interface": link.source_interface
                },
                "target": {
                    "node_id": str(link.target_node_id),
                    "interface": link.target_interface
                },
                "properties": {
                    "bandwidth": link.bandwidth,
                    "delay_ms": link.delay_ms,
                    "loss_percent": float(link.loss_percent) if link.loss_percent else 0,
                    "jitter_ms": link.jitter_ms
                },
                "status": link.status
            }
            for link in lab.links
        ],
        "created_at": lab.created_at.isoformat() if lab.created_at else None,
        "updated_at": lab.updated_at.isoformat() if lab.updated_at else None,
        "deployed_at": lab.deployed_at.isoformat() if lab.deployed_at else None
    }


@router.delete("/{lab_id}")
async def delete_lab(lab_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a lab
    """
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    db.delete(lab)
    db.commit()

    return {"message": "Lab deleted successfully"}


@router.post("/{lab_id}/nodes")
async def add_node_to_lab(
    lab_id: UUID,
    node: NodeCreate,
    db: Session = Depends(get_db)
):
    """
    Add a node to a lab
    """
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    db_node = Node(
        lab_id=lab_id,
        image_id=node.image_id,
        name=node.name,
        position_x=node.position_x,
        position_y=node.position_y,
        cpu=node.cpu,
        memory=node.memory,
        status="stopped"
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)

    return {
        "id": str(db_node.id),
        "name": db_node.name,
        "status": db_node.status
    }


@router.post("/{lab_id}/links")
async def add_link_to_lab(
    lab_id: UUID,
    link: LinkCreate,
    db: Session = Depends(get_db)
):
    """
    Add a link between two nodes in a lab
    """
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    db_link = Link(
        lab_id=lab_id,
        source_node_id=link.source_node_id,
        source_interface=link.source_interface,
        target_node_id=link.target_node_id,
        target_interface=link.target_interface,
        status="down"
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)

    return {
        "id": str(db_link.id),
        "status": db_link.status
    }


@router.post("/{lab_id}/deploy")
async def deploy_lab(
    lab_id: UUID,
    db: Session = Depends(get_db),
    runtime: RuntimeManager = Depends(get_runtime)
):
    """
    Deploy all nodes in a lab
    """
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    if lab.status == "running":
        return {"message": "Lab is already running", "status": "running"}

    try:
        # Update lab status
        lab.status = "deploying"
        db.commit()

        # Deploy each node
        deployed_nodes = []
        for node in lab.nodes:
            image = db.query(Image).filter(Image.id == node.image_id).first()
            if not image:
                raise HTTPException(
                    status_code=404,
                    detail=f"Image not found for node {node.name}"
                )

            result = await runtime.deploy_node(node, image, db)
            deployed_nodes.append({
                "node": node.name,
                "container_id": result["container_id"],
                "status": result["status"]
            })

        # Create links
        deployed_links = []
        for link in lab.links:
            result = await runtime.create_link(link, db)
            deployed_links.append({
                "link_id": str(link.id),
                "status": result["status"]
            })

        # Update lab status
        lab.status = "running"
        lab.deployed_at = datetime.utcnow()
        db.commit()

        return {
            "message": "Lab deployed successfully",
            "status": "running",
            "nodes": deployed_nodes,
            "links": deployed_links
        }

    except Exception as e:
        lab.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lab_id}/destroy")
async def destroy_lab(
    lab_id: UUID,
    db: Session = Depends(get_db),
    runtime: RuntimeManager = Depends(get_runtime)
):
    """
    Destroy all running nodes in a lab
    """
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    try:
        # Destroy each node
        for node in lab.nodes:
            if node.container_id:
                await runtime.destroy_node(node, db)

        # Update lab status
        lab.status = "stopped"
        db.commit()

        return {
            "message": "Lab destroyed successfully",
            "status": "stopped"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
