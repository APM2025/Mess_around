import requests

response = requests.post('http://127.0.0.1:5000/api/tables/table1',
                        json={'cohort_name': '12 months', 'year': 2024})

data = response.json()

print("Column order:")
for i, col in enumerate(data['data'][0].keys(), 1):
    print(f"{i}. {col}")

print("\nFirst row (UK):")
for k, v in data['data'][0].items():
    print(f"  {k}: {v}")
