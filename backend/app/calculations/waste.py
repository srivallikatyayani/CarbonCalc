def calculate_waste_emissions(kg: float | None) -> float:
    """
    Calculate waste emissions (Scope 3).
    Municipal/industrial waste factor: 0.45 kg CO₂e / kg
    """
    if kg is None or kg < 0:
        return 0.0
    return kg * 0.45
