from app.calculations.electricity import calculate_electricity_emissions
from app.calculations.fuel import calculate_fuel_emissions
from app.calculations.transport import calculate_transport_emissions
from app.calculations.waste import calculate_waste_emissions


def run_carbon_accounting_agent(data: dict) -> dict:
    """
    Agent 3: Carbon Accounting Agent.
    Computes Scopes 1, 2, 3 and compiles total carbon footprint.
    """
    # Scope 1: Fuel Combustion (Liters of Diesel/petrol)
    scope1 = calculate_fuel_emissions(data.get("fuel_liters"))
    
    # Scope 2: Purchased Electricity (kWh)
    scope2 = calculate_electricity_emissions(data.get("electricity_kwh"))
    
    # Scope 3: Travel and Waste (Flights + Transport + Waste generated)
    scope3 = calculate_transport_emissions(
        data.get("flights_taken"),
        data.get("transportation_km") or 0.0
    ) + calculate_waste_emissions(data.get("waste_generated_kg"))

    total = scope1 + scope2 + scope3

    return {
        "scope1_kg": scope1,
        "scope2_kg": scope2,
        "scope3_kg": scope3,
        "total_kg": total,
    }
