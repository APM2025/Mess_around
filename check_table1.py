import requests
import json

response = requests.post('http://127.0.0.1:5000/api/tables/table1',
                        json={'cohort_name': '12 months', 'year': 2024})

data = response.json()

print(f"Total rows: {len(data['data'])}")
print(f"\nAll geographic areas:")
for i, row in enumerate(data['data'], 1):
    print(f"{i}. {row['geographic_area']}")

print(f"\nFull data structure:")
print(json.dumps(data, indent=2))
