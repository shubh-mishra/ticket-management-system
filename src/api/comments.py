from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.database import get_db
from src.models.ticket import Ticket
from src.models.user import User
from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentResponse, CommentListResponse

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    ticket_id: UUID,
    comment_in: CommentCreate,
    db: Session = Depends(get_db)
):
    # Verify ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Verify author exists
    author = db.query(User).filter(User.id == comment_in.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author user not found")

    # Internal note guard: Only AGENT or ADMIN can create internal comments
    if comment_in.is_internal and author.role not in ["AGENT", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents and admins can create internal notes."
        )

    db_comment = Comment(
        ticket_id=ticket_id,
        author_id=comment_in.author_id,
        body=comment_in.body,
        is_internal=comment_in.is_internal
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/", response_model=CommentListResponse)
def list_comments(
    ticket_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    query = db.query(Comment).filter(Comment.ticket_id == ticket_id)
    total = query.count()
    comments = query.order_by(Comment.created_at.asc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": comments
    }