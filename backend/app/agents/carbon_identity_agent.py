def run_carbon_identity_agent(scope1: float, scope2: float, scope3: float, total: float) -> str:
    """
    Agent 6: Carbon Identity Agent.
    Categorizes the company into a distinct carbon personality based on source breakdown ratios:
    - Scope 2 (electricity) > 60% = Grid Dependent
    - Scope 1 (fuel) > 40% = Fossil Intensive
    - Scope 3 (transport/flights) > 40% = Logistics Heavy
    - Default/Balanced = Efficiency Pioneer
    """
    if total <= 0:
        return "Efficiency Pioneer"
        
    elec_ratio = scope2 / total
    fuel_ratio = scope1 / total
    scope3_ratio = scope3 / total
    
    if elec_ratio > 0.60:
        return "Grid Dependent"
    elif fuel_ratio > 0.40:
        return "Fossil Intensive"
    elif scope3_ratio > 0.40:
        return "Logistics Heavy"
    else:
        return "Efficiency Pioneer"
