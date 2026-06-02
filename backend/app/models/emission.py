"""
app/models/emission.py
──────────────────────
SQLAlchemy ORM model for the `emissions` table.

This model stores raw activity data submitted by a user or company.
It connects to the `users` table via a foreign key (`user_id`).

Column design decisions:
    id              → Integer surrogate PK.
    user_id         → Foreign key linking to the User who submitted this data.
    industry_type   → Company context (e.g., "Technology", "Manufacturing").
    electricity_kwh → Scope 2 emissions (purchased electricity).
    fuel_liters     → Scope 1 emissions (direct fuel combustion).
    flights_taken   → Scope 3 emissions (business travel).
    diet_type       → Individual Scope 3 (e.g., "Vegan", "Omnivore").
    waste_generated_kg → Scope 3 emissions (waste).
    month           → The month the activity took place (1-12).
    year            → The year the activity took place (e.g., 2026).
    created_at      → Set by the DATABASE server (func.now()).
    updated_at      → Auto-updated on every UPDATE by the DB engine.

Future relationships (added in later phases):
    carbon_footprint_kg → Calculated field (potentially added here, or in a separate table
                          managed by the Carbon Accounting Agent).
"""

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Emission(Base):
    """
    Represents a raw activity data submission for carbon footprint calculation.

    Table: emissions
    """

    __tablename__ = "emissions"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate primary key",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────────────
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The user or company this emission record belongs to",
    )

    # ── Activity Data ─────────────────────────────────────────────────────────
    industry_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Industry sector (e.g., Tech, Manufacturing) for companies",
    )

    electricity_kwh: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Purchased electricity in kilowatt-hours (Scope 2)",
    )

    fuel_liters: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Direct fuel combustion in liters (Scope 1)",
    )

    flights_taken: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of flights taken (Scope 3 - Travel)",
    )

    diet_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Dietary habits (e.g., Vegan, Meat-heavy) for individuals",
    )

    waste_generated_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Waste generated in kilograms (Scope 3)",
    )

    transportation_km: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Fleet transportation distance in kilometers (Scope 3)",
    )

    # ── Carbon Footprint Calculations (Calculated by Agents) ──────────────────
    scope1_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    scope2_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    scope3_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    personality: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Temporal Data ─────────────────────────────────────────────────────────
    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="The month of the activity (1-12)",
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="The year of the activity (e.g., 2026)",
    )

    # ── Audit Timestamps ──────────────────────────────────────────────────────
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp (UTC, set by database)",
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification timestamp (UTC, auto-updated by database)",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="emissions",
    )

    def __repr__(self) -> str:
        return f"<Emission id={self.id} user_id={self.user_id} period={self.year}-{self.month:02d}>"

    @property
    def indian_average_kg(self) -> float:
        from app.calculations.scoring import INDIAN_INDUSTRY_AVERAGES_KG
        return INDIAN_INDUSTRY_AVERAGES_KG.get(str(self.industry_type).lower().strip(), 18000.0)

    @property
    def percent_difference(self) -> float:
        avg = self.indian_average_kg
        total = self.total_kg or 0.0
        return ((total - avg) / avg) * 100.0

    @property
    def comparison_status(self) -> str:
        return "below_average" if self.percent_difference < 0 else "above_average"
