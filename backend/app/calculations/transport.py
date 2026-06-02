def calculate_transport_emissions(flights: int | None, km: float | None) -> float:
    """
    Calculate transport emissions (Scope 3).
    Flights factor: 250.0 kg CO₂e / flight
    Transportation fleet factor: 0.120 kg CO₂e / km
    """
    emissions = 0.0
    if flights is not None and flights > 0:
        emissions += flights * 250.0
    if km is not None and km > 0:
        emissions += km * 0.120
    return emissions
