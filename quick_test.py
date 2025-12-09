import requests

print("Quick visualization test for Table 1...")

# Test the endpoint with a simple request
payload = {
    "table_type": "table1",
    "cohort_name": "12 months",
    "year": 2024,
    "selected_areas": ["England", "Scotland", "Wales", "Northern Ireland"],
    "selected_vaccines": ["coverage_at_12_months_DTaP_IPV_Hib_HepB"]
}

print(f"\nSending to /api/visualize/table-comparison...")
resp = requests.post("http://localhost:5000/api/visualize/table-comparison", json=payload)

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"✅ Success: {resp.json()}")
else:
    print(f"❌ Error:")
    print(resp.text[:1000])
