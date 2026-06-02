def run_collection_agent(data: dict) -> dict:
    """
    Agent 1: Data Collection Agent.
    Sanitizes, checks types, and structures raw activity entries.
    """
    sanitized = {
        "user_id": int(data.get("user_id", 0)),
        "industry_type": str(data.get("industry_type", "manufacturing")).strip(),
        "electricity_kwh": float(data.get("electricity_kwh") or 0.0),
        "fuel_liters": float(data.get("fuel_liters") or 0.0),
        "flights_taken": int(data.get("flights_taken") or 0),
        "diet_type": str(data.get("diet_type") or "").strip() or None,
        "waste_generated_kg": float(data.get("waste_generated_kg") or 0.0),
        "month": int(data.get("month", 1)),
        "year": int(data.get("year", 2026)),
    }
    return sanitized
