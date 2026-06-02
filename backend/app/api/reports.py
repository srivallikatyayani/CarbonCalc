from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.emission import Emission
from app.models.user import User
from app.models.recommendation import Recommendation
from app.services.ml_service import get_user_emission_forecast
from app.calculations.scoring import calculate_carbon_score, get_indian_average_comparison

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

@router.get(
    "/sustainability",
    status_code=status.HTTP_200_OK,
    summary="Get aggregated sustainability report data",
)
def get_sustainability_report(
    user_id: int = Query(..., description="The user/company ID to compile the report for"),
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
        
    latest = db.query(Emission).filter(Emission.user_id == user_id).order_by(Emission.created_at.desc()).first()
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No emission metrics found for this user. Report cannot be compiled."
        )
        
    recs = db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
    
    # Calculate scores & comparisons
    total_kg = latest.total_kg or 0.0
    score = calculate_carbon_score(total_kg)
    comp = get_indian_average_comparison(latest.industry_type or "manufacturing", total_kg)
    
    # ML Forecasts
    latest_data = {
        "electricity_kwh": latest.electricity_kwh or 0.0,
        "fuel_liters": latest.fuel_liters or 0.0,
        "flights_taken": latest.flights_taken or 0,
        "waste_generated_kg": latest.waste_generated_kg or 0.0,
        "total_kg": total_kg
    }
    forecast = get_user_emission_forecast(user_id, latest_data)
    
    return {
        "company_name": user.name,
        "industry": latest.industry_type,
        "period": f"{latest.year}-{latest.month:02d}",
        "metrics": {
            "electricity_kwh": latest.electricity_kwh,
            "fuel_liters": latest.fuel_liters,
            "flights_taken": latest.flights_taken,
            "waste_generated_kg": latest.waste_generated_kg,
            "transportation_km": latest.transportation_km,
        },
        "scopes": {
            "scope1_kg": latest.scope1_kg,
            "scope2_kg": latest.scope2_kg,
            "scope3_kg": latest.scope3_kg,
            "total_kg": total_kg,
        },
        "carbon_score": score,
        "personality": latest.personality,
        "benchmarks": comp,
        "forecast": forecast,
        "recommendations": [
            {
                "title": r.title,
                "description": r.description,
                "reduction_pct": r.estimated_reduction_pct,
                "priority_score": r.priority_score
            }
            for r in recs
        ]
    }
