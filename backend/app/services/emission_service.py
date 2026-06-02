from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.models.emission import Emission
from app.models.recommendation import Recommendation
from app.agents.master_agent import run_sustainability_pipeline


def create_agentic_emission(db: Session, payload: dict) -> Emission:
    """
    Service layer: Emission creation driven by the 8-Agent pipeline.
    """
    user_id = payload["user_id"]
    
    stmt = select(Emission).where(Emission.user_id == user_id).order_by(Emission.created_at.asc())
    history_records = db.execute(stmt).scalars().all()
    
    history_data = []
    for rec in history_records:
        history_data.append({
            "electricity_kwh": rec.electricity_kwh,
            "fuel_liters": rec.fuel_liters,
            "flights_taken": rec.flights_taken,
            "waste_generated_kg": rec.waste_generated_kg,
            "transportation_km": rec.transportation_km,
            "total_kg": rec.total_kg,
        })
        
    pipeline_res = run_sustainability_pipeline(payload, history_data)
    
    sanitized = pipeline_res["sanitized_inputs"]
    accounting = pipeline_res["accounting"]
    personality = pipeline_res["personality"]
    recommendations = pipeline_res["recommendations"]
    
    db_emission = Emission(
        user_id=user_id,
        industry_type=sanitized["industry_type"],
        electricity_kwh=sanitized["electricity_kwh"],
        fuel_liters=sanitized["fuel_liters"],
        flights_taken=sanitized["flights_taken"],
        diet_type=sanitized["diet_type"],
        waste_generated_kg=sanitized["waste_generated_kg"],
        transportation_km=sanitized.get("transportation_km"),
        month=sanitized["month"],
        year=sanitized["year"],
        scope1_kg=accounting["scope1_kg"],
        scope2_kg=accounting["scope2_kg"],
        scope3_kg=accounting["scope3_kg"],
        total_kg=accounting["total_kg"],
        personality=personality
    )
    db.add(db_emission)
    db.flush()
    
    del_stmt = delete(Recommendation).where(Recommendation.user_id == user_id)
    db.execute(del_stmt)
    
    for rec in recommendations:
        db_rec = Recommendation(
            user_id=user_id,
            title=rec["title"],
            description=rec["description"],
            estimated_reduction_pct=rec["estimated_reduction_pct"],
            priority_score=rec["priority_score"]
        )
        db.add(db_rec)
        
    db.commit()
    db.refresh(db_emission)
    return db_emission
