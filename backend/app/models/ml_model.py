from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MLModel(Base):
    """
    SQLAlchemy ORM model for storing trained ML model metadata per user.
    """

    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mae_metric: Mapped[float] = mapped_column(Float, nullable=True)
    r2_score: Mapped[float] = mapped_column(Float, nullable=True)

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

    user: Mapped["User"] = relationship("User", back_populates="ml_models")

    def __repr__(self) -> str:
        return f"<MLModel id={self.id} user_id={self.user_id} path={self.model_path!r}>"
