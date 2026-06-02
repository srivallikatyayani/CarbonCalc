from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.recommendation import Recommendation


def get_user_recommendations(db: Session, user_id: int) -> list[Recommendation]:
    """
    Service layer: Retrieves saved recommendations for a given user.
    """
    stmt = select(Recommendation).where(Recommendation.user_id == user_id).order_by(Recommendation.priority_score.desc())
    return list(db.execute(stmt).scalars().all())
