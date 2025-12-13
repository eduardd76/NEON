"""
Images API endpoints
Manage network device images (routers, switches, firewalls, hosts)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.base import get_db
from app.db.models import Image, Vendor

router = APIRouter()


@router.get("/")
async def list_images(
    type: Optional[str] = None,
    vendor: Optional[str] = None,
    runtime: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List available network images with filtering

    - **type**: Filter by device type (router, switch, firewall, host)
    - **vendor**: Filter by vendor name
    - **runtime**: Filter by runtime (docker, qemu, vrnetlab)
    - **tag**: Filter by tag
    - **search**: Search in name and display_name
    """
    query = db.query(Image).filter(Image.is_active == True)

    if type:
        query = query.filter(Image.type == type)
    if vendor:
        query = query.join(Vendor).filter(Vendor.name == vendor)
    if runtime:
        query = query.filter(Image.runtime == runtime)
    if tag:
        query = query.filter(Image.tags.any(tag=tag))
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Image.display_name.ilike(search_pattern)) |
            (Image.name.ilike(search_pattern))
        )

    images = query.all()

    return {
        "count": len(images),
        "images": [
            {
                "id": str(img.id),
                "name": img.name,
                "display_name": img.display_name,
                "version": img.version,
                "type": img.type,
                "runtime": img.runtime,
                "image_uri": img.image_uri,
                "vendor": {
                    "name": img.vendor.name,
                    "display_name": img.vendor.display_name,
                    "logo_url": img.vendor.logo_url
                } if img.vendor else None,
                "cpu_recommended": img.cpu_recommended,
                "memory_recommended": img.memory_recommended,
                "startup_time": img.startup_time,
                "console_type": img.console_type,
                "default_credentials": img.default_credentials,
                "tags": [tag.tag for tag in img.tags]
            }
            for img in images
        ]
    }


@router.get("/{image_id}")
async def get_image(image_id: UUID, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific image
    """
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "id": str(image.id),
        "name": image.name,
        "display_name": image.display_name,
        "version": image.version,
        "description": image.description,
        "type": image.type,
        "category": image.category,
        "runtime": image.runtime,
        "image_uri": image.image_uri,
        "registry": image.registry,
        "vendor": {
            "id": str(image.vendor.id),
            "name": image.vendor.name,
            "display_name": image.vendor.display_name,
            "logo_url": image.vendor.logo_url,
            "website": image.vendor.website
        } if image.vendor else None,
        "resources": {
            "cpu_min": image.cpu_min,
            "cpu_recommended": image.cpu_recommended,
            "memory_min": image.memory_min,
            "memory_recommended": image.memory_recommended,
            "disk_size": image.disk_size
        },
        "behavior": {
            "startup_time": image.startup_time,
            "console_type": image.console_type,
            "default_credentials": image.default_credentials
        },
        "interfaces": {
            "definition": image.interfaces_definition,
            "max_interfaces": image.max_interfaces,
            "interfaces": [
                {
                    "name": intf.name,
                    "alias": intf.alias,
                    "type": intf.type,
                    "slot": intf.slot,
                    "port": intf.port
                }
                for intf in image.interfaces
            ]
        },
        "licensing": {
            "required": image.license_required,
            "info": image.license_info
        },
        "documentation_url": image.documentation_url,
        "notes": image.notes,
        "tags": [tag.tag for tag in image.tags],
        "is_verified": image.is_verified,
        "created_at": image.created_at.isoformat() if image.created_at else None,
        "updated_at": image.updated_at.isoformat() if image.updated_at else None
    }


@router.get("/vendors/")
async def list_vendors(db: Session = Depends(get_db)):
    """
    List all vendors
    """
    vendors = db.query(Vendor).all()

    return {
        "count": len(vendors),
        "vendors": [
            {
                "id": str(v.id),
                "name": v.name,
                "display_name": v.display_name,
                "logo_url": v.logo_url,
                "website": v.website,
                "image_count": len(v.images)
            }
            for v in vendors
        ]
    }
