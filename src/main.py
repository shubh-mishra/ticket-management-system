from fastapi import FastAPI
import src.models  # Crucial: ensures all models and relationships are registered
from src.api import tickets, comments

app = FastAPI(
    title="Ticket Management System API",
    version="1.0.0",
    description="Modular monolith ticket management system MVP built with FastAPI and SQLAlchemy."
)

# Include routers
app.include_router(tickets.router)
app.include_router(comments.router)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "message": "Ticket Management System API is running successfully!"
    }