import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.collection_agent import run_collection_agent
from app.agents.validation_agent import run_validation_agent
from app.agents.carbon_accounting_agent import run_carbon_accounting_agent
from app.agents.carbon_identity_agent import run_carbon_identity_agent
from app.agents.recommendation_agent import run_recommendation_agent
from app.agents.digital_twin_agent import run_digital_twin_agent
from app.agents.ml_training_agent import train_user_prediction_model, generate_synthetic_data
from app.agents.master_agent import run_sustainability_pipeline, run_copilot_chat

def main():
    print("--- Starting 8-Agent Platform Verification Test ---")
    
    raw_data = {
        "user_id": 1,
        "industry_type": "manufacturing",
        "electricity_kwh": 6500.0,
        "fuel_liters": 1500.0,
        "flights_taken": 3,
        "waste_generated_kg": 450.0,
        "month": 6,
        "year": 2026
    }
    
    print("\n[Agent 1: Collection] Running...")
    collected = run_collection_agent(raw_data)
    print("Collected Data:", collected)
    
    print("\n[Agent 2: Validation] Running bounds & anomaly checks...")
    history = [
        {
            "electricity_kwh": 4000.0,
            "fuel_liters": 900.0,
            "total_kg": 5000.0
        }
    ]
    val_res = run_validation_agent(collected, history)
    print("Validation Result (Valid?):", val_res["valid"])
    print("Validation Warnings (Anomaly MoM Jump?):", val_res["warnings"])
    
    print("\n[Agent 3: Carbon Accounting] Computing Scopes 1, 2, 3...")
    accounting = run_carbon_accounting_agent(collected)
    print("Scope Breakdown (kg CO2e):", accounting)
    collected.update(accounting)
    
    print("\n[Agent 4: User ML Agent] Generating synthetic training set...")
    synth_df = generate_synthetic_data([collected], target_rows=10)
    print(f"Generated {len(synth_df)} synthetic monthly rows.")
    print("First 3 synthetic rows:")
    print(synth_df[["electricity_kwh", "fuel_liters", "total_kg"]].head(3))
    
    print("\n[Agent 5: Personalized Prediction] Fitting RandomForestRegressor model...")
    ml_meta = train_user_prediction_model(1, [collected])
    print("Model Path:", ml_meta["model_path"])
    print("Model MAE:", ml_meta["mae"])
    print("Model R2 Score:", ml_meta["r2"])
    
    print("\n[Agent 6: Carbon Identity] Assigning Dynamically Classified Tag...")
    personality = run_carbon_identity_agent(
        collected["scope1_kg"],
        collected["scope2_kg"],
        collected["scope3_kg"],
        collected["total_kg"]
    )
    print("Assigned Carbon Personality:", personality)
    
    print("\n[Agent 7: Recommendations] Compiling customized energy savings tips...")
    recs = run_recommendation_agent(personality)
    print(f"Generated {len(recs)} prioritized sustainability recommendation(s). Top one:")
    print(recs[0])
    
    print("\n[Agent 8: Digital Twin] Simulating -20% Electricity & -15% Fuel Scenario...")
    twin_res = run_digital_twin_agent(collected, {
        "electricity_pct": 20.0,
        "fuel_pct": 15.0,
        "waste_pct": 0.0,
        "transport_pct": 0.0
    })
    print("Original Footprint (kg):", twin_res["original"]["total_kg"])
    print("Simulated Footprint (kg):", twin_res["simulated"]["total_kg"])
    print("Carbon Savings (kg):", twin_res["reduction_kg"])
    print("Potential Cost Savings (INR):", twin_res["financial_savings_inr"])
    
    print("\n[Master Agent: Chat Copilot] Conversing with user...")
    chat_reply = run_copilot_chat(1, "What if I reduce my electricity by 20%?", collected, personality)
    print("User Prompt: 'What if I reduce my electricity by 20%?'")
    print("Copilot Agent Response:")
    print(chat_reply)
    
    print("\n--- All 8 Agents Verified and Executed Successfully! ---")

if __name__ == "__main__":
    main()
