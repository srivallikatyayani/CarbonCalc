from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Recommendation(Base):
    """
    SQLAlchemy ORM model for dynamic sustainability recommendations.
    """

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_reduction_pct: Mapped[float] = mapped_column(Float, nullable=False)
    priority_score: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation id={self.id} user_id={self.user_id} title={self.title!r}>"
