def calculate_fuel_emissions(liters: float | None) -> float:
    """
    Calculate fuel combustion emissions (Scope 1).
    Diesel emission factor: 2.675 kg CO₂e / Liter
    """
    if liters is None or liters < 0:
        return 0.0
    return liters * 2.675
