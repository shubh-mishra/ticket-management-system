import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="CUSTOMER")  # CUSTOMER, AGENT, ADMIN
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tickets_created = relationship("Ticket", foreign_keys="[Ticket.created_by_id]", back_populates="creator")
    tickets_assigned = relationship("Ticket", foreign_keys="[Ticket.assigned_to_id]", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")