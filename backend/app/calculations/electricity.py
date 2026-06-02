def calculate_electricity_emissions(kwh: float | None) -> float:
    """
    Calculate electricity emissions (Scope 2).
    Indian grid emission factor: 0.710 kg CO₂e / kWh
    """
    if kwh is None or kwh < 0:
        return 0.0
    return kwh * 0.710
