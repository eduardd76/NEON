from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class LabSession(Base):
    __tablename__ = "lab_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_id = Column(UUID(as_uuid=True), ForeignKey("labs.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    action = Column(String(50), nullable=False)  # deploy, destroy, save, export
    details = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lab = relationship("Lab", back_populates="sessions")
    user = relationship("User", back_populates="lab_sessions")

    def __repr__(self):
        return f"<LabSession(action='{self.action}', created_at='{self.created_at}')>"
