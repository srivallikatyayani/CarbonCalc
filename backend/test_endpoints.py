import os
import sys
import random
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

def main():
    print("=== STARTING END-TO-END ENDPOINT INTEGRATION TESTS ===")
    client = TestClient(app)
    
    # Generate unique test user
    rand_id = random.randint(1000, 9999)
    email = f"company_{rand_id}@test.com"
    user_payload = {
        "name": f"Test Company {rand_id}",
        "email": email,
        "password": "secure_password_123"
    }
    
    # 1. POST /api/v1/users/ (User Registration)
    print("\n1. Testing POST /api/v1/users/ (User Registration)...")
    res_user = client.post("/api/v1/users/", json=user_payload)
    if res_user.status_code != 201:
        print(f"FAILED: User registration returned {res_user.status_code}: {res_user.text}")
        return
    user_data = res_user.json()
    user_id = user_data["id"]
    print(f"SUCCESS: Created user {user_id} ({user_data['email']})")
    
    # 1b. POST /api/v1/auth/login (User Authentication)
    print("\n1b. Testing POST /api/v1/auth/login (Authentication)...")
    login_payload = {
        "email": email,
        "password": "secure_password_123"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    if res_login.status_code != 200:
        print(f"FAILED: User login returned {res_login.status_code}: {res_login.text}")
        return
    login_data = res_login.json()
    print(f"SUCCESS: Authenticated user {login_data['id']} ({login_data['email']})")

    # 1c. PUT /api/v1/users/{id}/industry (User Industry Selection)
    print("\n1c. Testing PUT /api/v1/users/{id}/industry (Industry Selection)...")
    ind_payload = {
        "industry_type": "manufacturing"
    }
    res_ind = client.put(f"/api/v1/users/{user_id}/industry", json=ind_payload)
    if res_ind.status_code != 200:
        print(f"FAILED: Industry update returned {res_ind.status_code}: {res_ind.text}")
        return
    ind_data = res_ind.json()
    print(f"SUCCESS: Selected industry '{ind_data['industry_type']}' for user {user_id}")

    # 2. GET /api/v1/users/ (User Listing)
    print("\n2. Testing GET /api/v1/users/ (User Listing)...")
    res_list = client.get("/api/v1/users/")
    if res_list.status_code != 200:
        print(f"FAILED: User list returned {res_list.status_code}")
        return
    list_data = res_list.json()
    print(f"SUCCESS: Total users count in DB = {list_data['count']}")
    
    # 3. POST /api/v1/emissions/ (Data Submission & 8-Agent Pipeline Orchestration)
    print("\n3. Testing POST /api/v1/emissions/ (Orchestrating 8-Agent Pipeline)...")
    emission_payload = {
        "user_id": user_id,
        "industry_type": "manufacturing",
        "electricity_kwh": 7200.0,
        "fuel_liters": 1600.0,
        "flights_taken": 2,
        "waste_generated_kg": 350.0,
        "month": 6,
        "year": 2026
    }
    res_em = client.post("/api/v1/emissions/", json=emission_payload)
    if res_em.status_code != 201:
        print(f"FAILED: Emission submission returned {res_em.status_code}: {res_em.text}")
        return
    em_data = res_em.json()
    print(f"SUCCESS: Agentic pipeline executed successfully.")
    print(f"Calculated Scopes - Scope 1: {em_data['scope1_kg']:.1f} kg, Scope 2: {em_data['scope2_kg']:.1f} kg, Scope 3: {em_data['scope3_kg']:.1f} kg")
    print(f"Total Carbon Footprint: {em_data['total_kg']:.1f} kg CO2e")
    print(f"Assigned Carbon Personality: {em_data['personality']}")
    print(f"National Average Comparison: Industry avg = {em_data['indian_average_kg']} kg, Diff = {em_data['percent_difference']:.1f}%, Status = {em_data['comparison_status']}")
    
    # 4. GET /api/v1/emissions/ (List emissions with filter)
    print("\n4. Testing GET /api/v1/emissions/ (Historical retrieval)...")
    res_hist = client.get(f"/api/v1/emissions/?user_id={user_id}")
    if res_hist.status_code != 200:
        print(f"FAILED: GET emissions returned {res_hist.status_code}")
        return
    hist_data = res_hist.json()
    print(f"SUCCESS: Retrieved {hist_data['count']} records for user {user_id}")

    # 4b. GET /api/v1/emissions/forecast (ML prediction / forecasting)
    print("\n4b. Testing GET /api/v1/emissions/forecast (ML Emission Forecasting)...")
    res_fore = client.get(f"/api/v1/emissions/forecast?user_id={user_id}")
    if res_fore.status_code != 200:
        print(f"FAILED: GET forecast returned {res_fore.status_code}: {res_fore.text}")
        return
    fore_data = res_fore.json()
    print(f"SUCCESS: ML Forecasting executed successfully. Status = {fore_data['model_status']}")
    print(f"  - Projected 1-Month Emission: {fore_data['forecast_1m_kg']:.1f} kg CO2e")
    print(f"  - Projected 3-Month Emission: {fore_data['forecast_3m_kg']:.1f} kg CO2e")
    
    # 5. GET /api/v1/recommendations/ (Prioritized recommendations retrieval)
    print("\n5. Testing GET /api/v1/recommendations/ (Prioritized recommendations retrieval)...")
    res_recs = client.get(f"/api/v1/recommendations/?user_id={user_id}")
    if res_recs.status_code != 200:
        print(f"FAILED: GET recommendations returned {res_recs.status_code}")
        return
    recs_data = res_recs.json()
    print(f"SUCCESS: Retrieved {len(recs_data)} prioritized recommendations.")
    for i, r in enumerate(recs_data, 1):
        print(f"  [{i}] {r['title']} (Reduction Potential: {r['estimated_reduction_pct']}%, Priority Score: {r['priority_score']})")
        
    # 6. POST /api/v1/simulator/ (Digital Twin Simulation what-if scenario)
    print("\n6. Testing POST /api/v1/simulator/ (Digital Twin Simulation what-if)...")
    sim_payload = {
        "user_id": user_id,
        "electricity_pct": 20.0,
        "fuel_pct": 10.0,
        "waste_pct": 0.0,
        "transport_pct": 0.0
    }
    res_sim = client.post("/api/v1/simulator/", json=sim_payload)
    if res_sim.status_code != 200:
        print(f"FAILED: Twin simulation returned {res_sim.status_code}")
        return
    sim_res = res_sim.json()
    print(f"SUCCESS: Simulated Savings = {sim_res['reduction_kg']:.1f} kg CO2e, Financial Savings = INR {sim_res['financial_savings_inr']:,.2f}")
    
    # 6b. GET /api/v1/reports/sustainability (Aggregated Sustainability Report)
    print("\n6b. Testing GET /api/v1/reports/sustainability (Aggregated Sustainability Audit Report)...")
    res_rep = client.get(f"/api/v1/reports/sustainability?user_id={user_id}")
    if res_rep.status_code != 200:
        print(f"FAILED: Sustainability report returned {res_rep.status_code}: {res_rep.text}")
        return
    rep_data = res_rep.json()
    print(f"SUCCESS: Sustainability Audit Report compiled for {rep_data['company_name']}")
    print(f"  - Operational Sector: {rep_data['industry']}")
    print(f"  - Scopes Audit - Scope 1: {rep_data['scopes']['scope1_kg']:.1f} kg, Scope 2: {rep_data['scopes']['scope2_kg']:.1f} kg, Scope 3: {rep_data['scopes']['scope3_kg']:.1f} kg")
    print(f"  - Carbon Scoring: {rep_data['carbon_score']} / 100 ({rep_data['personality']})")
    print(f"  - Total Prioritized Recommendations: {len(rep_data['recommendations'])}")

    # 7. POST /api/v1/copilot/chat (AI Sustainability Copilot Chat dialog)
    print("\n7. Testing POST /api/v1/copilot/chat (Copilot dialog simulation)...")
    chat_payload = {
        "user_id": user_id,
        "message": "What if we reduce electricity by 30%?"
    }
    res_chat = client.post("/api/v1/copilot/chat", json=chat_payload)
    if res_chat.status_code != 200:
        print(f"FAILED: Copilot chat returned {res_chat.status_code}")
        return
    chat_data = res_chat.json()
    print("SUCCESS: Copilot replied successfully:")
    print("--- Copilot Response ---")
    print(chat_data["reply"])
    print("------------------------")
    
    print("\n=== ALL ENDPOINT INTEGRATION TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
