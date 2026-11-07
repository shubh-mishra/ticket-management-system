from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1)
    is_internal: bool = Field(default=False)
    author_id: UUID

class CommentResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    author_id: UUID
    body: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    total: int
    items: List[CommentResponse]