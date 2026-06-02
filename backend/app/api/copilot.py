from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.models.emission import Emission
from app.agents.master_agent import run_copilot_chat

router = APIRouter(
    prefix="/copilot",
    tags=["Sustainability Copilot"],
)


class ChatRequest(BaseModel):
    user_id: int = Field(..., description="The user/company ID chatting")
    message: str = Field(..., description="The user question to the copilot")


@router.post(
    "/chat",
    status_code=status.HTTP_200_OK,
    summary="Chat with the Sustainability Copilot",
)
def chat_with_copilot(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Intelligent chatbot agent query endpoint.
    Processes what-if simulations, general guidance, and recommends solar/EV solutions.
    """
    latest = db.query(Emission).filter(Emission.user_id == payload.user_id).order_by(Emission.created_at.desc()).first()
    
    if not latest:
        latest_data = {
            "electricity_kwh": 5000.0,
            "fuel_liters": 1200.0,
            "flights_taken": 2,
            "waste_generated_kg": 400.0,
            "total_kg": 6915.0
        }
        personality = "Efficiency Pioneer"
    else:
        latest_data = {
            "electricity_kwh": latest.electricity_kwh or 0.0,
            "fuel_liters": latest.fuel_liters or 0.0,
            "flights_taken": latest.flights_taken or 0,
            "waste_generated_kg": latest.waste_generated_kg or 0.0,
            "total_kg": latest.total_kg or 0.0
        }
        personality = latest.personality or "Efficiency Pioneer"
        
    reply = run_copilot_chat(payload.user_id, payload.message, latest_data, personality)
    return {"reply": reply}
