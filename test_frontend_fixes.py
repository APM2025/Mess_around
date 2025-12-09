"""
Quick test script to verify CRUD and visualization endpoints work
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_table1_load():
    """Test loading Table 1 data"""
    print("Testing Table 1 load...")
    response = requests.post(f"{BASE_URL}/api/tables/table1", 
                            json={"cohort_name": "12 months", "year": 2024})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Table 1 loaded successfully: {len(data.get('data', []))} rows")
        return data
    else:
        print(f"✗ Error loading Table 1: {response.status_code}")
        print(response.text)
        return None

def test_visualization(table_data):
    """Test visualization generation for Table 1"""
    print("\nTesting Table 1 visualization...")
    
    if not table_data or not table_data.get('data'):
        print("✗ No table data to visualize")
        return False
    
    # Get all coverage columns
    first_row = table_data['data'][0]
    coverage_cols = [col for col in first_row.keys() if col.startswith('coverage_at_')]
    areas = [row.get('geographic_area', '') for row in table_data['data']]
    
    print(f"  - Found {len(coverage_cols)} coverage columns")
    print(f"  - Found {len(areas)} areas")
    
    response = requests.post(f"{BASE_URL}/api/visualize/table-comparison",
                            json={
                                "table_type": "table1",
                                "cohort_name": "12 months",
                                "year": 2024,
                                "selected_areas": areas,
                                "selected_vaccines": coverage_cols
                            })
    
    if response.status_code == 200:
        result = response.json()
        if 'error' in result:
            print(f"✗ Visualization error: {result['error']}")
            return False
        else:
            print(f"✓ Visualization generated: {result.get('chart_url', 'N/A')}")
            return True
    else:
        print(f"✗ Error generating visualization: {response.status_code}")
        print(response.text[:200])
        return False

def test_crud_get_areas():
    """Test getting areas for CRUD"""
    print("\nTesting CRUD - Get Areas...")
    response = requests.get(f"{BASE_URL}/api/areas")
    if response.status_code == 200:
        areas = response.json()
        print(f"✓ Retrieved {len(areas)} areas")
        return areas
    else:
        print(f"✗ Error getting areas: {response.status_code}")
        return None

def test_crud_update_row():
    """Test updating a row via CRUD"""
    print("\nTesting CRUD - Update Row...")
    
    # Test with England data
    test_payload = {
        "area_code": "E92000001",  # England
        "year": 2024,
        "cohort_name": "12 months",
        "vaccine_data": [
            {
                "vaccine_code": "DTaP_IPV_Hib_HepB",
                "eligible_population": 100000,
                "vaccinated_count": 95000,
                "coverage_percentage": 95.0
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/crud/row",
                            json=test_payload,
                            headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Row update successful: {result.get('message', 'OK')}")
        return True
    else:
        print(f"✗ Error updating row: {response.status_code}")
        print(response.text[:300])
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Frontend Fixes")
    print("=" * 60)
    
    # Test 1: Load Table 1
    table_data = test_table1_load()
    
    # Test 2: Visualization
    if table_data:
        test_visualization(table_data)
    
    # Test 3: CRUD - Get Areas
    test_crud_get_areas()
    
    # Test 4: CRUD - Update Row
    test_crud_update_row()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
