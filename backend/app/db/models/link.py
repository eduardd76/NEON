from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_id = Column(UUID(as_uuid=True), ForeignKey("labs.id", ondelete="CASCADE"))

    # Endpoints
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"))
    source_interface = Column(String(50), nullable=False)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"))
    target_interface = Column(String(50), nullable=False)

    # Link properties (for impairment)
    bandwidth = Column(String(20))  # '1Gbps', '10Gbps'
    delay_ms = Column(Integer, default=0)
    loss_percent = Column(Numeric(5, 2), default=0)
    jitter_ms = Column(Integer, default=0)

    # State: up, down
    status = Column(String(20), default="down")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lab = relationship("Lab", back_populates="links")
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="source_links")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="target_links")

    def __repr__(self):
        return f"<Link(source='{self.source_interface}', target='{self.target_interface}')>"
