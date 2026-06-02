import os
import pickle
import pandas as pd
from app.agents.collection_agent import run_collection_agent
from app.agents.validation_agent import run_validation_agent
from app.agents.carbon_accounting_agent import run_carbon_accounting_agent
from app.agents.ml_training_agent import train_user_prediction_model
from app.agents.carbon_identity_agent import run_carbon_identity_agent
from app.agents.recommendation_agent import run_recommendation_agent
from app.agents.digital_twin_agent import run_digital_twin_agent


def run_sustainability_pipeline(data: dict, history: list[dict]) -> dict:
    """
    Master Agent pipeline runner.
    Flows raw inputs through Agents 1 to 7 sequentially:
    1. Collection Agent: structures/sanitizes inputs
    2. Validation Agent: checks ranges, alerts on anomaly jumps
    3. Carbon Accounting Agent: computes scopes 1, 2, 3 and totals
    4. User ML & Prediction Agents (ml_training_agent): fits model on synthetic + real data
    5. Carbon Identity Agent: assigns facility Carbon Personality
    6. Recommendation Agent: generates customized priority recommendations
    """
    collected = run_collection_agent(data)
    user_id = collected["user_id"]
    
    validation_res = run_validation_agent(collected, history)
    warnings = validation_res["warnings"]
    
    accounting_res = run_carbon_accounting_agent(collected)
    collected.update(accounting_res)
    
    full_history = history + [collected]
    ml_res = train_user_prediction_model(user_id, full_history)
    
    personality = run_carbon_identity_agent(
        collected["scope1_kg"],
        collected["scope2_kg"],
        collected["scope3_kg"],
        collected["total_kg"]
    )
    
    recommendations = run_recommendation_agent(personality)
    
    return {
        "user_id": user_id,
        "sanitized_inputs": collected,
        "validation_warnings": warnings,
        "accounting": accounting_res,
        "personality": personality,
        "recommendations": recommendations,
        "ml_metadata": ml_res
    }


def run_copilot_chat(user_id: int, message: str, current_record: dict, personality: str) -> str:
    """
    Sustainability Copilot Agent.
    Intelligently parses queries and responds based on actual twin details.
    """
    msg = message.lower()
    
    if "what if" in msg or "simulate" in msg or "reduce" in msg:
        elec_pct = 0.0
        fuel_pct = 0.0
        
        if "electricity" in msg or "power" in msg:
            if "20%" in msg or "20 percent" in msg: elec_pct = 20.0
            elif "30%" in msg or "30 percent" in msg: elec_pct = 30.0
            elif "10%" in msg or "10 percent" in msg: elec_pct = 10.0
            else: elec_pct = 15.0
            
        if "fuel" in msg or "diesel" in msg:
            if "20%" in msg: fuel_pct = 20.0
            elif "30%" in msg: fuel_pct = 30.0
            else: fuel_pct = 15.0
            
        twin_res = run_digital_twin_agent(current_record, {
            "electricity_pct": elec_pct,
            "fuel_pct": fuel_pct,
            "waste_pct": 0.0,
            "transport_pct": 0.0
        })
        
        saved_kg = twin_res["reduction_kg"]
        saved_inr = twin_res["financial_savings_inr"]
        
        return (
            f"[Digital Twin Simulator] Digital Twin Simulation initiated:\n"
            f"Reducing electricity by {elec_pct}% and fuel by {fuel_pct}% would decrease your monthly footprint by "
            f"**{saved_kg:.1f} kg CO2e** (a reduction of **{twin_res['reduction_pct']:.1f}%**).\n"
            f"This translates to **INR {saved_inr:,.2f}** in monthly commercial savings!"
        )
        
    if "recommend" in msg or "advice" in msg or "how" in msg or "solar" in msg:
        if personality == "Grid Dependent":
            return (
                f"[Recommendations] Personalized Recommendations:\n"
                f"As a **Grid Dependent** facility, your primary focus should be offsetting purchased electricity.\n"
                f"I highly recommend: **Installing Rooftop Solar Panels in Chennai** (High Priority Score: 9.5). Chennai offers excellent solar exposure, which can cut your electricity footprint by up to 25%!"
            )
        elif personality == "Fossil Intensive":
            return (
                f"[Recommendations] Personalized Recommendations:\n"
                f"Your facility is flagged as **Fossil Intensive** due to diesel combustion. "
                f"Focus on converting forklifts and transport fleet to Electric Vehicles (EVs) (Estimated reduction: 18%)."
            )
        elif personality == "Logistics Heavy":
            return (
                f"[Recommendations] Personalized Recommendations:\n"
                f"As a **Logistics Heavy** facility, fleet operations and shipping represent your primary footprint.\n"
                f"I highly recommend: **Consolidating Shipments & Algorithmic Route Optimization** (Priority Score: 8.2), which can cut fleet logistics emissions by up to 12%!"
            )
        else:
            return (
                f"[Recommendations] Personalized Recommendations:\n"
                f"I highly recommend: **Procuring Green Energy Tariffs / PPAs** to offset operational electricity, and introducing **Strict Solid Waste Segregation** to divert compostable organics from landfills (Priority Score: 9.0)."
            )
            
    return (
        f"Hello! I am your AI Sustainability Copilot.\n"
        f"Your facility currently has a **{personality}** carbon personality with a footprint of "
        f"**{current_record.get('total_kg', 0.0):,.1f} kg CO2e**. "
        f"Ask me to 'simulate a 20% reduction in electricity' or ask for 'recommendations' to see how we can reduce your footprint!"
    )
