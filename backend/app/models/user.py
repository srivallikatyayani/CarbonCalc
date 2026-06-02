"""
app/models/user.py
──────────────────
SQLAlchemy ORM model for the `users` table.

This is the central identity record for the entire CarbonCalc platform.
Every other domain object (Emission, Recommendation, MLModel, DigitalTwin)
will have a foreign key pointing back to `users.id`.

Column design decisions:
    id              → Integer surrogate PK. Simple, fast, and compatible with
                       all future FK references in emissions/recommendations.
    name            → String(100): bounded to prevent unbounded storage.
    email           → String(255): RFC 5321 max is 254 chars. Unique index
                       ensures one account per address and speeds up login queries.
    hashed_password → String(255): bcrypt output is 60 chars, but 255 gives
                       room if the hashing algorithm is ever upgraded.
    is_active       → Boolean soft-delete flag. Deactivating a user preserves
                       all FK-linked emissions data instead of cascading deletes.
    created_at      → Set by the DATABASE server (func.now()), not Python.
                       Immune to clock skew between app servers.
    updated_at      → Auto-updated on every UPDATE by the DB engine. The
                       ML recommendation pipeline uses this to detect profiles
                       that have changed and need re-scoring.

Future relationships (added in later phases):
    emissions       → One-to-many: User → Emission records
    recommendations → One-to-many: User → Recommendation records
    ml_profiles     → One-to-one:  User → MLProfile (feature store)
    digital_twin    → One-to-one:  User → DigitalTwin simulation state
"""

# pyrefly: ignore [missing-import]
from sqlalchemy import Boolean, DateTime, Integer, String, func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    """
    Represents a registered user (individual or company account).

    Table: users
    """

    __tablename__ = "users"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate primary key",
    )

    # ── Identity ──────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name of the user or company",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,            # Index speeds up login query: WHERE email = ?
        comment="Unique email address used as login identity",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt hash — plaintext password is never stored",
    )

    industry_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Primary industry sector selected by company",
    )

    # ── Status ────────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Soft-delete flag. False = deactivated, emissions data preserved",
    )

    # ── Audit Timestamps ──────────────────────────────────────────────────────
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by PostgreSQL, not Python
        nullable=False,
        comment="Record creation timestamp (UTC, set by database)",
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),        # Auto-updated on every UPDATE statement
        nullable=False,
        comment="Last modification timestamp (UTC, auto-updated by database)",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    emissions: Mapped[list["Emission"]] = relationship(
        "Emission",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    ml_models: Mapped[list["MLModel"]] = relationship(
        "MLModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} active={self.is_active}>"
