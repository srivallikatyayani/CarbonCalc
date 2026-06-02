"""
app/database/init_db.py
───────────────────────
Table creation and database initialisation script.

How SQLAlchemy table creation works:
    Base.metadata.create_all(engine) inspects Base.metadata.tables — a
    registry of all ORM model classes that have been defined.

    CRITICAL: A model is only registered when its module is IMPORTED.
    If User is never imported here, the `users` table will never be created,
    and create_all() will silently do nothing.

    This file's imports are therefore not redundant — they are the
    explicit registration step that populates Base.metadata.

Idempotency:
    create_all() uses "CREATE TABLE IF NOT EXISTS" semantics.
    Running this multiple times is always safe — existing tables and
    data are never dropped or altered.

    For schema CHANGES (adding columns, changing types), use Alembic
    migrations — not create_all(). Alembic will be introduced in a
    later phase when the schema is stable.

When is this called?
    1. main.py lifespan startup event  → automatic on server boot
    2. python -m app.database.init_db  → manual CLI invocation for setup

Future:
    As new models are added (Emission, Recommendation, MLModel, DigitalTwin),
    import them here. They will be created automatically on next startup.
"""

from app.database.base import Base
from app.database.connection import engine, test_connection

# ── Model imports (registration triggers) ────────────────────────────────────
# Each import registers the model's table with Base.metadata.
# Add new models here as the platform grows.
from app.models.user import User  # noqa: F401 — import is intentional
from app.models.emission import Emission  # noqa: F401
from app.models.recommendation import Recommendation  # noqa: F401
from app.models.ml_model import MLModel  # noqa: F401


def init_db() -> None:
    """
    Create all registered tables in PostgreSQL.

    Called automatically from main.py's lifespan context on server startup.
    Also callable manually via: python -m app.database.init_db
    """
    print("[init_db] Initialising database...")

    # Verify connectivity before attempting DDL
    if not test_connection():
        raise RuntimeError(
            "Cannot initialise database: PostgreSQL is not reachable. "
            "Check DATABASE_URL in your .env file."
        )

    # Create all tables registered in Base.metadata
    Base.metadata.create_all(bind=engine)
    print("[init_db] Database tables created (or already exist)")
    print(f"[init_db] Tables: {list(Base.metadata.tables.keys())}")


# ── Standalone CLI ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
