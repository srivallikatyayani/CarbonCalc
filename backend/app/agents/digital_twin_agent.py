from app.calculations.electricity import calculate_electricity_emissions
from app.calculations.fuel import calculate_fuel_emissions
from app.calculations.transport import calculate_transport_emissions
from app.calculations.waste import calculate_waste_emissions


def run_digital_twin_agent(original_data: dict, factors: dict) -> dict:
    """
    Agent 8: Digital Twin Agent.
    Simulates what-if scenarios based on percentage reductions:
    - electricity_pct (e.g. 20 for 20% reduction)
    - fuel_pct
    - waste_pct
    - transport_pct
    Calculates future footprint and financial savings:
    - Electricity cost: ₹8 per kWh
    - Fuel cost: ₹100 per Liter of diesel
    """
    elec_red = float(factors.get("electricity_pct") or 0.0) / 100.0
    fuel_red = float(factors.get("fuel_pct") or 0.0) / 100.0
    waste_red = float(factors.get("waste_pct") or 0.0) / 100.0
    trans_red = float(factors.get("transport_pct") or 0.0) / 100.0

    orig_elec = float(original_data.get("electricity_kwh") or 0.0)
    orig_fuel = float(original_data.get("fuel_liters") or 0.0)
    orig_waste = float(original_data.get("waste_generated_kg") or 0.0)
    orig_flights = int(original_data.get("flights_taken") or 0)
    orig_transport_km = float(original_data.get("transportation_km") or 0.0)

    sim_elec = orig_elec * (1.0 - elec_red)
    sim_fuel = orig_fuel * (1.0 - fuel_red)
    sim_waste = orig_waste * (1.0 - waste_red)
    sim_flights = int(orig_flights * (1.0 - trans_red))
    sim_transport_km = orig_transport_km * (1.0 - trans_red)

    sim_scope1 = calculate_fuel_emissions(sim_fuel)
    sim_scope2 = calculate_electricity_emissions(sim_elec)
    sim_scope3 = calculate_transport_emissions(sim_flights, sim_transport_km) + calculate_waste_emissions(sim_waste)
    sim_total = sim_scope1 + sim_scope2 + sim_scope3

    orig_scope1 = calculate_fuel_emissions(orig_fuel)
    orig_scope2 = calculate_electricity_emissions(orig_elec)
    orig_scope3 = calculate_transport_emissions(orig_flights, orig_transport_km) + calculate_waste_emissions(orig_waste)
    orig_total = orig_scope1 + orig_scope2 + orig_scope3

    elec_savings_inr = (orig_elec - sim_elec) * 8.0
    fuel_savings_inr = (orig_fuel - sim_fuel) * 100.0
    total_savings_inr = elec_savings_inr + fuel_savings_inr

    return {
        "original": {
            "scope1_kg": orig_scope1,
            "scope2_kg": orig_scope2,
            "scope3_kg": orig_scope3,
            "total_kg": orig_total
        },
        "simulated": {
            "scope1_kg": sim_scope1,
            "scope2_kg": sim_scope2,
            "scope3_kg": sim_scope3,
            "total_kg": sim_total
        },
        "reduction_kg": max(orig_total - sim_total, 0.0),
        "reduction_pct": (max(orig_total - sim_total, 0.0) / orig_total * 100.0) if orig_total > 0 else 0.0,
        "financial_savings_inr": total_savings_inr
    }
