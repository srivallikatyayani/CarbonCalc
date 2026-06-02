"""
app/api/emissions.py
────────────────────
FastAPI router for the Emissions domain.

Handles HTTP requests related to user activity data submission and retrieval.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Query, status
# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.emission import Emission
from app.models.user import User
from app.schemas.emission import EmissionCreate, EmissionListResponse, EmissionResponse

router = APIRouter(
    prefix="/emissions",
    tags=["Emissions"],
)


@router.post(
    "/",
    response_model=EmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new emission record",
    description="Submit raw activity data for a specific user. (User ID is required in the body until auth is implemented.)",
)
def create_emission(
    payload: EmissionCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new emission record.
    """
    # 1. Verify that the requested user exists
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {payload.user_id} not found.",
        )

    # 2. Check if the user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add emissions to an inactive user account.",
        )

    # 3. Create and compute the emission via the 8-Agent master pipeline
    from app.services.emission_service import create_agentic_emission
    db_emission = create_agentic_emission(db, payload.model_dump())

    return db_emission


@router.get(
    "/",
    response_model=EmissionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all emission records",
    description="Retrieve a paginated list of all emissions. Optionally filter by user_id.",
)
def get_emissions(
    user_id: int | None = Query(None, description="Filter emissions by a specific user ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve emissions.
    """
    stmt = select(Emission).order_by(Emission.created_at.desc())
    
    # Apply user_id filter if provided
    if user_id is not None:
        stmt = stmt.where(Emission.user_id == user_id)
        
    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt)
    emissions = result.scalars().all()

    return EmissionListResponse(
        count=len(emissions),
        emissions=list(emissions)
    )


@router.get(
    "/forecast",
    status_code=status.HTTP_200_OK,
    summary="Get user emission forecast",
)
def fetch_forecast(
    user_id: int = Query(..., description="The user/company ID to get forecasts for"),
    db: Session = Depends(get_db)
):
    """
    Get 1-month and 3-month forecasts using personalized Random Forest or fallback metrics.
    """
    latest = db.query(Emission).filter(Emission.user_id == user_id).order_by(Emission.created_at.desc()).first()
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No emission history found for user {user_id}. Please submit activity data first.",
        )
        
    latest_data = {
        "electricity_kwh": latest.electricity_kwh or 0.0,
        "fuel_liters": latest.fuel_liters or 0.0,
        "flights_taken": latest.flights_taken or 0,
        "waste_generated_kg": latest.waste_generated_kg or 0.0,
        "total_kg": latest.total_kg or 0.0
    }
    
    from app.services.ml_service import get_user_emission_forecast
    forecast = get_user_emission_forecast(user_id, latest_data)
    return forecast
