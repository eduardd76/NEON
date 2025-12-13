from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"))

    # Basic Info
    name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    version = Column(String(50))
    description = Column(Text)

    # Classification
    type = Column(String(50), nullable=False, index=True)  # router, switch, firewall, host
    category = Column(String(50))

    # Runtime
    runtime = Column(String(20), nullable=False, default="docker", index=True)
    image_uri = Column(String(500), nullable=False)
    registry = Column(String(200))

    # Resource Requirements
    cpu_min = Column(Integer, default=1)
    cpu_recommended = Column(Integer, default=2)
    memory_min = Column(Integer, default=512)  # MB
    memory_recommended = Column(Integer, default=2048)  # MB
    disk_size = Column(Integer, default=4096)  # MB

    # Behavior
    startup_time = Column(Integer, default=30)  # seconds
    console_type = Column(String(20), default="ssh")
    default_credentials = Column(JSONB)

    # Interfaces
    interfaces_definition = Column(JSONB)
    max_interfaces = Column(Integer, default=16)

    # Licensing
    license_required = Column(Boolean, default=False)
    license_info = Column(Text)

    # Documentation
    documentation_url = Column(String(500))
    notes = Column(Text)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vendor = relationship("Vendor", back_populates="images")
    interfaces = relationship("ImageInterface", back_populates="image", cascade="all, delete-orphan")
    tags = relationship("ImageTag", back_populates="image", cascade="all, delete-orphan")
    nodes = relationship("Node", back_populates="image")

    def __repr__(self):
        return f"<Image(name='{self.name}', version='{self.version}', type='{self.type}')>"


class ImageInterface(Base):
    __tablename__ = "image_interfaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"))

    name = Column(String(50), nullable=False)
    alias = Column(String(50))
    type = Column(String(30), default="ethernet")
    slot = Column(Integer, default=0)
    port = Column(Integer, nullable=False)
    linux_mapping = Column(String(50))

    # Relationships
    image = relationship("Image", back_populates="interfaces")

    def __repr__(self):
        return f"<ImageInterface(name='{self.name}', type='{self.type}')>"


class ImageTag(Base):
    __tablename__ = "image_tags"

    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), primary_key=True)
    tag = Column(String(50), nullable=False, primary_key=True)

    # Relationships
    image = relationship("Image", back_populates="tags")

    def __repr__(self):
        return f"<ImageTag(tag='{self.tag}')>"
