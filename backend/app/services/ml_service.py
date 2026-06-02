import os
import pickle
import numpy as np


def get_user_emission_forecast(user_id: int, current_record: dict) -> dict:
    """
    Service layer: Loads the user's custom ML model and generates emission forecasts.
    Returns projected emissions for:
    - 1 month out
    - 3 months out
    """
    model_path = os.path.join("app", "ml", "saved_models", f"user_{user_id}_model.pkl")
    
    elec = float(current_record.get("electricity_kwh") or 5000.0)
    fuel = float(current_record.get("fuel_liters") or 1200.0)
    flights = int(current_record.get("flights_taken") or 2)
    waste = float(current_record.get("waste_generated_kg") or 400.0)
    
    if os.path.exists(model_path):
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
                
            inputs_1m = np.array([[elec * 1.03, fuel * 1.03, flights, waste * 1.03]])
            inputs_3m = np.array([[elec * 1.09, fuel * 1.09, flights, waste * 1.09]])
            
            pred_1m = float(model.predict(inputs_1m)[0])
            pred_3m = float(model.predict(inputs_3m)[0])
            
            return {
                "forecast_1m_kg": pred_1m,
                "forecast_3m_kg": pred_3m,
                "model_status": "personalized_forest"
            }
        except Exception as exc:
            print(f"[ml_service] Error loading model: {exc}")
            
    current_total = float(current_record.get("total_kg") or 6915.0)
    return {
        "forecast_1m_kg": current_total * 1.03,
        "forecast_3m_kg": current_total * 1.09,
        "model_status": "analytical_fallback"
    }
