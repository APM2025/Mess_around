
import sys
import os
sys.path.append(os.getcwd())
import logging

# Configure basic logging to catch everything
logging.basicConfig(level=logging.DEBUG)

try:
    from app import app
    from flask import json
    
    # Create test client
    client = app.test_client()
    
    # Mock payload for Table 1 visualization
    payload = {
        "table_type": "table1",
        "cohort_name": "24 months",
        "year": 2024,
        "selected_areas": ["England", "Scotland"], 
        # Note: Table 1 usually has specific areas in geographic_area like "England", "Scotland"
        # We need to make sure we select ones that exist.
        "selected_vaccines": ["coverage_at_24_months_DTaP_IPV_Hib"] 
        # Note: Need a valid column name. I'll pick one common one or check table first.
    }
    
    # Helper to get valid Table 1 column
    print("Fetching Table 1 data to find valid columns...")
    t1_resp = client.post('/api/tables/table1', 
                         data=json.dumps({"cohort_name": "24 months", "year": 2024}),
                         content_type='application/json')
    
    if t1_resp.status_code == 200:
        t1_data = json.loads(t1_resp.data)
        if t1_data['data']:
            first_row = t1_data['data'][0]
            # Find a coverage column
            cov_cols = [k for k in first_row.keys() if k.startswith('coverage_at_')]
            if cov_cols:
                print(f"Found coverage columns: {cov_cols[:2]}...")
                payload['selected_vaccines'] = [cov_cols[0]]
                
                # Also find valid areas
                areas = [r.get('geographic_area') or r.get('local_authority') for r in t1_data['data'][:3]]
                payload['selected_areas'] = areas
                print(f"Testing with areas: {areas}")
    
    print("\nTesting Visualization Endpoint...")
    response = client.post('/api/visualize/table-comparison', 
                          data=json.dumps(payload),
                          content_type='application/json')
                          
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.content_type}")
    
    if response.status_code != 200:
        print("Error Response Body:")
        print(response.data.decode('utf-8'))
    else:
        print("Success response:")
        print(response.data.decode('utf-8'))
        
except Exception as e:
    print(f"CRITICAL ERROR IN SCRIPT: {e}")
    import traceback
    traceback.print_exc()
