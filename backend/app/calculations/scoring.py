INDIAN_INDUSTRY_AVERAGES_KG = {
    "dairy": 12000.0,
    "manufacturing": 25000.0,
    "agriculture": 8000.0,
    "textile": 15000.0,
    "automobile": 30000.0,
}

def calculate_carbon_score(total_emissions_kg: float) -> int:
    """
    Translate absolute carbon footprint (kg CO2e) to a normalized score [0, 100].
    0 = green/excellent, 100 = critical/extremely high footprint.
    Using a standard benchmark where 15,000 kg is average/medium (score 50),
    scaled linearly up to 30,000 kg.
    """
    if total_emissions_kg <= 0:
        return 0
    score = int((total_emissions_kg / 30000.0) * 100.0)
    return min(max(score, 1), 100)

def get_indian_average_comparison(industry_type: str, total_emissions_kg: float) -> dict:
    """
    Compare total footprint to national averages.
    """
    avg = INDIAN_INDUSTRY_AVERAGES_KG.get(str(industry_type).lower().strip(), 18000.0)
    percent_diff = ((total_emissions_kg - avg) / avg) * 100.0
    return {
        "indian_average_kg": avg,
        "percent_difference": percent_diff,
        "comparison_status": "below_average" if percent_diff < 0 else "above_average"
    }
