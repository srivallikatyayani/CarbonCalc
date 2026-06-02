"""
app/database/session.py
───────────────────────
Session factory and FastAPI dependency for database access.

Architecture:
    SessionLocal   → The factory. Call SessionLocal() to get a new Session.
    get_db()       → A FastAPI dependency generator. Injects a Session into
                     any endpoint that declares `db: Session = Depends(get_db)`.

Session lifecycle per request:
    1. FastAPI calls next(get_db()) → SessionLocal() is created, yielded
    2. Endpoint runs with the session
    3. If endpoint succeeds    → caller commits (explicit, in service layer)
    4. If exception is raised  → finally block closes session (SQLAlchemy
                                 auto-rolls back uncommitted transactions)
    5. finally: db.close()     → connection returned to pool

Why autocommit=False (the default)?
    Every database write is wrapped in a transaction automatically.
    Nothing is persisted until db.commit() is called explicitly.
    This gives full control: you can inspect the state before committing,
    and rollback cleanly if validation fails after the write.

Why autoflush=False?
    Prevents SQLAlchemy from issuing premature SQL flushes when you access
    relationships or run queries within the same session. Explicit is better
    than implicit in a production API.

Future usage:
    - Every endpoint in app/api/ uses `db: Session = Depends(get_db)`
    - LangGraph agent nodes that need DB access will use get_db directly
    - Background tasks (Celery) will call SessionLocal() manually and
      manage their own commit/rollback lifecycle
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import engine

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # Explicit commits — nothing persists without db.commit()
    autoflush=False,    # No implicit flushes — queries won't trigger premature SQL
    expire_on_commit=False,  # ORM objects stay usable after commit (no lazy reload)
)


# ── FastAPI Dependency ────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session for the duration
    of a single HTTP request.

    Usage in any endpoint:
        from sqlalchemy.orm import Session
        from fastapi import Depends
        from app.database.session import get_db

        @router.post("/")
        def create_something(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
