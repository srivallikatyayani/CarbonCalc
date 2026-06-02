def run_recommendation_agent(personality: str, city: str = "Chennai") -> list[dict]:
    """
    Agent 7: Recommendation Agent.
    Generates structured, customized energy saving recommendations based on the
    facility's personality and regional context (e.g. Solar feasibility in Chennai).
    Returns a list of recommendations, each with title, description, reduction pct, and priority score.
    """
    recommendations = []
    
    if personality == "Grid Dependent":
        recommendations.append({
            "title": f"Install Rooftop Solar Panels in {city}",
            "description": f"Chennai and South India have highly abundant solar irradiance. Swapping 30% of your grid power for clean, decentralized rooftop solar yields massive carbon and commercial savings.",
            "estimated_reduction_pct": 25.0,
            "priority_score": 9.5
        })
        recommendations.append({
            "title": "Upgrade to Energy-Efficient LED Lighting",
            "description": "Retrofitting fluorescent lamps with smart commercial LEDs cuts lighting power demand by up to 60% with an immediate payback period.",
            "estimated_reduction_pct": 5.0,
            "priority_score": 8.0
        })
        recommendations.append({
            "title": "Optimize HVAC / Chiller Operations",
            "description": "Set office AC temperatures to 24°C instead of 18°C. Regular filter maintenance and smart thermostats prevent chiller cycle shorting.",
            "estimated_reduction_pct": 8.0,
            "priority_score": 7.5
        })
    elif personality == "Fossil Intensive":
        recommendations.append({
            "title": "Transition Logistics Fleet to Electric Vehicles (EVs)",
            "description": "Electrifying last-mile distribution or factory forklifts bypasses diesel combustion entirely, charging using standard grid/solar assets.",
            "estimated_reduction_pct": 18.0,
            "priority_score": 8.8
        })
        recommendations.append({
            "title": "Conduct Boiler/Furnace Combustion Efficiency Tuning",
            "description": "Conduct exhaust gas oxygen tuning. Keeping oxygen levels below 3% optimizes fuel combustion ratios and cuts direct fuel consumption.",
            "estimated_reduction_pct": 6.0,
            "priority_score": 7.8
        })
    elif personality == "Logistics Heavy":
        recommendations.append({
            "title": "Consolidate Shipments and Optimize Supply Chain Routing",
            "description": "Grouping shipping batches and using algorithmic routing ensures vehicles run at maximum load capacity and travel minimum distances.",
            "estimated_reduction_pct": 12.0,
            "priority_score": 8.2
        })
        recommendations.append({
            "title": "Implement 'Virtual Meetings First' Policy",
            "description": "Mandate virtual channels for all non-critical quarterly inter-city meetings. Reducing business flights lowers high-altitude carbon footprints.",
            "estimated_reduction_pct": 15.0,
            "priority_score": 7.6
        })
    else:
        recommendations.append({
            "title": "Procure Green Energy Tariffs / PPAs",
            "description": "Sign a Power Purchase Agreement (PPA) with local wind or solar independent power producers to cover core operational electricity.",
            "estimated_reduction_pct": 15.0,
            "priority_score": 9.0
        })
        recommendations.append({
            "title": "Introduce Strict Solid Waste Segregation",
            "description": "Separate organic and recyclable waste streams. Composting organics avoids landfill methane, while recycling captures embedded material values.",
            "estimated_reduction_pct": 4.0,
            "priority_score": 8.5
        })

    recommendations.sort(key=lambda r: r["priority_score"], reverse=True)
    return recommendations
