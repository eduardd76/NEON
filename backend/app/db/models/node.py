from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_id = Column(UUID(as_uuid=True), ForeignKey("labs.id", ondelete="CASCADE"))
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"))

    # Identity
    name = Column(String(100), nullable=False)
    hostname = Column(String(100))

    # Position on canvas
    position_x = Column(Integer, default=100)
    position_y = Column(Integer, default=100)

    # Resources (override image defaults)
    cpu = Column(Integer)
    memory = Column(Integer)

    # Runtime state: stopped, starting, running, error
    status = Column(String(30), default="stopped", index=True)
    container_id = Column(String(100))
    mgmt_ip = Column(INET)
    console_port = Column(Integer)

    # Configuration
    startup_config = Column(Text)
    running_config = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    lab = relationship("Lab", back_populates="nodes")
    image = relationship("Image", back_populates="nodes")
    source_links = relationship(
        "Link",
        foreign_keys="Link.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )
    target_links = relationship(
        "Link",
        foreign_keys="Link.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Node(name='{self.name}', status='{self.status}')>"
