"""
app/database/connection.py
──────────────────────────
Provides the SQLAlchemy Engine — the single source of truth for the
connection pool shared by the entire application.

Architectural note:
    This module deliberately performs NO I/O at import time.
    The engine is a lazy connection pool — it only opens a real TCP
    connection to PostgreSQL when a query is actually executed.

    test_connection() is kept as an explicit callable so that:
      - startup health checks can call it intentionally
      - unit tests can mock or skip it without hitting the real DB
      - importing this module from workers / agents has zero side-effects

Future usage:
    - app/database/session.py      → imports `engine` to build SessionLocal
    - app/database/init_db.py      → imports `engine` to run create_all()
    - Future: Alembic migrations will reference `engine` for env.py
"""

from sqlalchemy import create_engine, text

from app.core.config import DATABASE_URL

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: SQLAlchemy tests each connection from the pool with a
# cheap "SELECT 1" before handing it to a session.  This silently recycles
# stale connections (e.g. after PostgreSQL restarts) instead of raising errors.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ── Health-check utility ──────────────────────────────────────────────────────
def test_connection() -> bool:
    """
    Explicitly verify that the database is reachable.

    Returns True on success, False on failure.
    Call this from init_db.py or a /health endpoint — never at import time.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[db] PostgreSQL connected successfully")
        return True
    except Exception as exc:
        print(f"[db] Connection failed: {exc}")
        return False


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_connection()