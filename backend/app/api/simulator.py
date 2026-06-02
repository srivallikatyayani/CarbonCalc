from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.models.emission import Emission
from app.agents.digital_twin_agent import run_digital_twin_agent

router = APIRouter(
    prefix="/simulator",
    tags=["Digital Twin Simulator"],
)


class SimulationRequest(BaseModel):
    user_id: int = Field(..., description="The user/company ID running the twin")
    electricity_pct: float = Field(0.0, ge=0, le=100)
    fuel_pct: float = Field(0.0, ge=0, le=100)
    waste_pct: float = Field(0.0, ge=0, le=100)
    transport_pct: float = Field(0.0, ge=0, le=100)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Run what-if simulation",
)
def run_simulation(payload: SimulationRequest, db: Session = Depends(get_db)):
    """
    Agent 8: Digital Twin Agent.
    Simulates reduction potentials based on percentage adjustments.
    """
    latest = db.query(Emission).filter(Emission.user_id == payload.user_id).order_by(Emission.created_at.desc()).first()
    
    if not latest:
        latest_data = {
            "electricity_kwh": 5000.0,
            "fuel_liters": 1200.0,
            "flights_taken": 2,
            "waste_generated_kg": 400.0,
            "transportation_km": 1000.0,
            "total_kg": 6915.0
        }
    else:
        latest_data = {
            "electricity_kwh": latest.electricity_kwh or 0.0,
            "fuel_liters": latest.fuel_liters or 0.0,
            "flights_taken": latest.flights_taken or 0,
            "waste_generated_kg": latest.waste_generated_kg or 0.0,
            "transportation_km": latest.transportation_km or 0.0,
            "total_kg": latest.total_kg or 0.0
        }
        
    twin_res = run_digital_twin_agent(latest_data, payload.model_dump())
    return twin_res
