import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


def generate_synthetic_data(history: list[dict], target_rows: int = 100) -> pd.DataFrame:
    """
    Agent 4: User ML Agent (Synthetic Data Generation).
    If real data is too sparse, duplicate and add controlled Gaussian noise to compile 100+ training rows.
    """
    if not history:
        history = [{
            "electricity_kwh": 5000.0,
            "fuel_liters": 1200.0,
            "flights_taken": 2,
            "waste_generated_kg": 400.0,
            "total_kg": 6915.0
        }]
        
    df_base = pd.DataFrame(history)
    features = ["electricity_kwh", "fuel_liters", "flights_taken", "waste_generated_kg"]
    
    records = []
    np.random.seed(42)
    for _ in range(target_rows):
        base_row = df_base.sample(n=1).iloc[0]
        new_row = base_row.copy()
        
        for feat in features:
            if feat in base_row and base_row[feat] is not None:
                val = float(base_row[feat])
                std = max(val * 0.1, 1.0)
                noise = np.random.normal(0, std)
                new_row[feat] = max(val + noise, 0.0)
                
        elec_kg = new_row.get("electricity_kwh", 0) * 0.710
        fuel_kg = new_row.get("fuel_liters", 0) * 2.675
        waste_kg = new_row.get("waste_generated_kg", 0) * 0.45
        flights_kg = new_row.get("flights_taken", 0) * 250.0
        new_row["total_kg"] = elec_kg + fuel_kg + waste_kg + flights_kg
        
        records.append(new_row)
        
    return pd.DataFrame(records)


def train_user_prediction_model(user_id: int, history: list[dict]) -> dict:
    """
    Agent 5: Personalized Prediction Agent.
    Trains a RandomForestRegressor model exclusively for the company/user,
    measures performance metrics, and saves the binary pkl file.
    """
    df_train = generate_synthetic_data(history, target_rows=120)
    
    X_train = df_train[["electricity_kwh", "fuel_liters", "flights_taken", "waste_generated_kg"]]
    y_train = df_train["total_kg"]
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_train)
    mae = float(mean_absolute_error(y_train, predictions))
    r2 = float(r2_score(y_train, predictions))
    
    model_dir = os.path.join("app", "ml", "saved_models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"user_{user_id}_model.pkl")
    
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        
    return {
        "model_path": model_path,
        "mae": mae,
        "r2": r2
    }
