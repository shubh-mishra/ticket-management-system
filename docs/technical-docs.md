# Technical Documentation - Ticket Management System

## Directory Structure & File Responsibilities

### `src/core/`
- **`database.py`**: Initializes the SQLAlchemy engine, creates the session maker (`SessionLocal`), defines declarative `Base`, and provides the `get_db()` FastAPI dependency.

### `src/models/`
- **`user.py`**: User entity mapping (`id`, `email`, `role` [CUSTOMER/AGENT/ADMIN]).
- **`team.py`**: Team grouping entity mapping (`id`, `name`).
- **`ticket.py`**: Core ticket entity mapping (`id`, `title`, `description`, `status`, `priority`, foreign keys).
- **`comment.py`**: Communication thread entity mapping (`id`, `body`, `is_internal`, `ticket_id`, `author_id`).

### `src/schemas/`
- **`ticket.py`**: Pydantic validation schemas for request bodies (`TicketCreate`) and serialization responses (`TicketResponse`).

### `src/api/`
- **`tickets.py`**: FastAPI router handling ticket endpoints (`POST /tickets`, `GET /tickets`, etc.).

### Root Files
- **`src/main.py`**: FastAPI application entry point, middleware wiring, and router registration.
- **`alembic.ini` & `alembic/`**: Database migration environment configuration and version history.