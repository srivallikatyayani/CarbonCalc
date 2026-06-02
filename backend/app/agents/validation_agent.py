def run_validation_agent(current_data: dict, history: list[dict]) -> dict:
    """
    Agent 2: Validation Agent.
    Checks:
    - Values < 0 (reject)
    - Total emissions month-over-month jumps of > 50% compared to history (warn/flag)
    """
    # 1. Bounds checks
    fields_to_check = ["electricity_kwh", "fuel_liters", "flights_taken", "waste_generated_kg"]
    for field in fields_to_check:
        val = current_data.get(field, 0)
        if val < 0:
            raise ValueError(f"Validation failure: Field '{field}' cannot be negative ({val}).")

    warnings = []
    
    # 2. Historical anomaly checks
    if history:
        last_month = history[-1]
        for field in ["electricity_kwh", "fuel_liters"]:
            current_val = current_data.get(field, 0.0)
            hist_val = last_month.get(field, 0.0)
            if hist_val > 0:
                pct_change = (current_val - hist_val) / hist_val
                if pct_change >= 0.50:
                    warnings.append(
                        f"Anomaly Flag: Sudden {pct_change:.1%} jump in {field} "
                        f"({current_val:.1f} vs previous {hist_val:.1f})."
                    )
                    
    return {
        "valid": True,
        "warnings": warnings,
        "data": current_data
    }
