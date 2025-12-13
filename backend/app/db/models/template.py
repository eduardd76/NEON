from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # NULL for system templates

    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)  # datacenter, wan, campus, sp

    # Template content
    topology_yaml = Column(Text, nullable=False)

    # Display
    thumbnail_url = Column(String(500))
    icon = Column(String(50))

    # Visibility
    is_public = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False)

    # Stats
    usage_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="templates")

    def __repr__(self):
        return f"<Template(name='{self.name}', category='{self.category}')>"
