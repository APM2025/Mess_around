"""Quick test script to verify table API endpoints."""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_utla_table():
    """Test UTLA table endpoint."""
    print("=" * 70)
    print("Testing UTLA Table API")
    print("=" * 70)

    response = requests.post(
        f"{BASE_URL}/api/tables/utla",
        json={"cohort_name": "24 months", "year": 2024}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Cohort: {data['cohort']}")
        print(f"Year: {data['year']}")
        print(f"Row Count: {data['row_count']}")

        if data['data']:
            print(f"\nFirst row sample:")
            first_row = data['data'][0]
            for key, value in list(first_row.items())[:5]:
                print(f"  {key}: {value}")
            print("  ...")
    else:
        print(f"Error: {response.text}")
    print()


def test_regional_table():
    """Test regional table endpoint."""
    print("=" * 70)
    print("Testing Regional Table API")
    print("=" * 70)

    response = requests.post(
        f"{BASE_URL}/api/tables/regional",
        json={"cohort_name": "24 months"}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Cohort: {data['cohort']}")
        print(f"Row Count: {data['row_count']}")

        if data['data']:
            print(f"\nFirst row sample:")
            first_row = data['data'][0]
            for key, value in first_row.items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {response.text}")
    print()


def test_england_summary():
    """Test England summary endpoint."""
    print("=" * 70)
    print("Testing England Summary API")
    print("=" * 70)

    response = requests.post(
        f"{BASE_URL}/api/tables/england-summary",
        json={"cohort_name": "24 months", "year": 2024}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Area: {data.get('area_name', 'N/A')}")
        print(f"Cohort: {data.get('cohort', 'N/A')}")
        print(f"Year: {data.get('year', 'N/A')}")

        if data.get('vaccines'):
            print(f"\nVaccines ({len(data['vaccines'])}):")
            for vaccine in data['vaccines'][:5]:
                print(f"  {vaccine['vaccine_code']}: {vaccine['coverage_percentage']}%")
    else:
        print(f"Error: {response.text}")
    print()


if __name__ == "__main__":
    print("\nTesting Table Builder API Endpoints")
    print("=" * 70)
    print()

    try:
        test_utla_table()
        test_regional_table()
        test_england_summary()

        print("=" * 70)
        print("All tests completed!")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Flask server.")
        print("Please ensure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
