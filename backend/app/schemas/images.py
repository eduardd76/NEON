"""
Pydantic schemas for Images API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class VendorBase(BaseModel):
    name: str
    display_name: str
    logo_url: Optional[str] = None
    website: Optional[str] = None


class VendorResponse(VendorBase):
    id: UUID
    image_count: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImageBase(BaseModel):
    name: str
    display_name: str
    version: Optional[str] = None
    description: Optional[str] = None
    type: str
    runtime: str = "docker"
    image_uri: str
    cpu_min: Optional[int] = 1
    cpu_recommended: Optional[int] = 2
    memory_min: Optional[int] = 512
    memory_recommended: Optional[int] = 2048
    startup_time: Optional[int] = 30
    console_type: Optional[str] = "ssh"


class ImageCreate(ImageBase):
    vendor_id: UUID
    default_credentials: Optional[Dict[str, str]] = None
    interfaces_definition: Optional[Dict] = None


class VendorSummary(BaseModel):
    name: str
    display_name: str
    logo_url: Optional[str] = None


class ImageResponse(ImageBase):
    id: UUID
    vendor: VendorSummary
    default_credentials: Optional[Dict[str, str]] = None
    tags: List[str] = []
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    count: int
    images: List[ImageResponse]


class VendorListResponse(BaseModel):
    count: int
    vendors: List[VendorResponse]
