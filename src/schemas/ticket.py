from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|URGENT)$")
    team_id: Optional[UUID] = None
    created_by_id: UUID  # References one of our seeded customer UUIDs

class TicketResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    priority: str
    created_by_id: UUID
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    total: int
    items: List[TicketResponse]
    skip: int
    limit: int

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    status: Optional[str] = Field(None, pattern="^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$")
    priority: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|URGENT)$")
    assigned_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None