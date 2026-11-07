import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="OPEN", index=True)       # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(50), nullable=False, default="MEDIUM", index=True)   # LOW, MEDIUM, HIGH, URGENT
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = relationship("User", foreign_keys=[created_by_id], back_populates="tickets_created")
    assignee = relationship("User", foreign_keys=[assigned_to_id], back_populates="tickets_assigned")
    team = relationship("Team", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_ticket_search', 'title', 'description'),
    )