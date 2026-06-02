from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.recommendation_service import get_user_recommendations

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get personalized recommendations",
)
def fetch_recommendations(
    user_id: int = Query(..., description="The user/company ID to fetch recommendations for"),
    db: Session = Depends(get_db)
):
    """
    Agent 7: Recommendation Agent.
    Retrieves the custom energy savings options saved for this facility.
    """
    recs = get_user_recommendations(db, user_id)
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "estimated_reduction_pct": r.estimated_reduction_pct,
            "priority_score": r.priority_score
        }
        for r in recs
    ]
