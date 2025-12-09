import requests
import json

# Get Table 1 data
resp = requests.post("http://localhost:5000/api/tables/table1", 
                    json={"cohort_name": "12 months", "year": 2024})

data = resp.json()
print("Table 1 structure:")
print(json.dumps(data, indent=2)[:1000])

if data.get('data'):
    print("\nFirst row:")
    first = data['data'][0]
    print(json.dumps(first, indent=2))
    
    print("\nKeys in first row:")
    for key in first.keys():
        print(f"  - {key}: {first[key]}")
