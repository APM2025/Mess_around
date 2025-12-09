import requests
import json

# Test Table 1 visualization
print("Testing Table 1 Visualization...")

# First get table data
response = requests.post("http://localhost:5000/api/tables/table1", 
                        json={"cohort_name": "12 months", "year": 2024})

if response.status_code != 200:
    print(f"Error loading table: {response.status_code}")
    print(response.text)
    exit(1)

table_data = response.json()
print(f"Table loaded: {len(table_data.get('data', []))} rows")

# Check data structure
if table_data.get('data'):
    first_row = table_data['data'][0]
    print(f"\nFirst row keys: {list(first_row.keys())}")
    
    # Find coverage columns
    coverage_cols = [k for k in first_row.keys() if k.startswith('coverage_at_')]
    print(f"\nCoverage columns found: {len(coverage_cols)}")
    for col in coverage_cols:
        print(f"  - {col}")
    
    # Get areas
    areas = [row.get('geographic_area', '') for row in table_data['data']]
    print(f"\nAreas: {areas}")
    
    # Try visualization
    print("\n" + "="*60)
    print("Attempting visualization...")
    
    viz_request = {
        "table_type": "table1",
        "cohort_name": "12 months",
        "year": 2024,
        "selected_areas": areas,
        "selected_vaccines": coverage_cols
    }
    
    print(f"Request payload:")
    print(json.dumps(viz_request, indent=2))
    
    viz_response = requests.post("http://localhost:5000/api/visualize/table-comparison",
                                json=viz_request)
    
    print(f"\nResponse status: {viz_response.status_code}")
    
    if viz_response.status_code == 200:
        result = viz_response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        if 'error' in result:
            print(f"\n❌ Visualization error: {result['error']}")
        else:
            print(f"\n✅ Visualization successful!")
    else:
        print(f"\n❌ HTTP Error: {viz_response.status_code}")
        print(viz_response.text[:500])
