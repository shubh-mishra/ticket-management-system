from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.ticket import Ticket
from src.models.user import User
from src.schemas.ticket import TicketCreate, TicketResponse, TicketListResponse, TicketUpdate
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    # Verify creator user exists
    creator = db.query(User).filter(User.id == ticket_in.created_by_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator user not found")

    db_ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        status="OPEN",
        created_by_id=ticket_in.created_by_id,
        team_id=ticket_in.team_id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.get("/", response_model=TicketListResponse)
def list_tickets(
    status: Optional[str] = Query(None, description="Filter by ticket status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)"),
    priority: Optional[str] = Query(None, description="Filter by ticket priority (LOW, MEDIUM, HIGH, URGENT)"),
    search: Optional[str] = Query(None, description="Search term across title and description"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    # Apply status filter
    if status:
        query = query.filter(Ticket.status == status.upper())

    # Apply priority filter
    if priority:
        query = query.filter(Ticket.priority == priority.upper())

    # Apply text search across title or description
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Ticket.title.ilike(search_pattern)) | 
            (Ticket.description.ilike(search_pattern))
        )

    # Get total count before pagination
    total = query.count()

    # Apply pagination and ordering
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": tickets,
        "skip": skip,
        "limit": limit
    }


# Allowed state transition map
VALID_TRANSITIONS = {
    "OPEN": ["IN_PROGRESS", "CLOSED"],
    "IN_PROGRESS": ["RESOLVED", "OPEN"],
    "RESOLVED": ["CLOSED", "IN_PROGRESS"],
    "CLOSED": [] # Terminal state
}

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: UUID, ticket_in: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Validate state machine transition if status is being updated
    if ticket_in.status and ticket_in.status != ticket.status:
        allowed_next_states = VALID_TRANSITIONS.get(ticket.status, [])
        if ticket_in.status not in allowed_next_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{ticket.status}' to '{ticket_in.status}'. Allowed transitions: {allowed_next_states}"
            )
        ticket.status = ticket_in.status

    # Validate assignee if provided
    if ticket_in.assigned_to_id:
        assignee = db.query(User).filter(User.id == ticket_in.assigned_to_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee user not found")
        ticket.assigned_to_id = ticket_in.assigned_to_id

    # Update other fields if provided
    if ticket_in.title is not None:
        ticket.title = ticket_in.title
    if ticket_in.description is not None:
        ticket.description = ticket_in.description
    if ticket_in.priority is not None:
        ticket.priority = ticket_in.priority
    if ticket_in.team_id is not None:
        ticket.team_id = ticket_in.team_id

    db.commit()
    db.refresh(ticket)
    return ticket