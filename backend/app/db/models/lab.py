from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Lab(Base):
    __tablename__ = "labs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Status: draft, deploying, running, stopped, error
    status = Column(String(30), default="draft", index=True)

    # Topology YAML representation
    topology_yaml = Column(Text)

    # Metadata
    tags = Column(ARRAY(String(50)))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deployed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="labs")
    nodes = relationship("Node", back_populates="lab", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="lab", cascade="all, delete-orphan")
    sessions = relationship("LabSession", back_populates="lab", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lab(name='{self.name}', status='{self.status}')>"
