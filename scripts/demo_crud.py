"""
Demo script showing all CRUD operations with vaccination data.

NOTE: This script requires a populated database at data/vaccination_coverage.db
Run create_database.py first to populate data before running this script.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database_version_2.src.database import get_session
from database_version_2.src.crud import VaccinationCRUD


def main():
    """Demonstrate all CRUD operations."""
    try:
        session = get_session()
        crud = VaccinationCRUD(session)

        print("=" * 70)
        print("CRUD OPERATIONS DEMO")
        print("=" * 70)

        # CREATE operations
        print("\n[CREATE] Creating new records...")
        print("-" * 70)

        # Create a test area
        print("\n1. Creating a new geographic area:")
        new_area = crud.create_geographic_area(
            area_code='E99999999',
            area_name='Test Demo Area',
            area_type='utla'
        )
        print(f"   Created: {new_area.area_name} ({new_area.area_code})")

        # Create a test vaccine
        print("\n2. Creating a new vaccine:")
        new_vaccine = crud.create_vaccine(
            vaccine_code='DEMO1',
            vaccine_name='Demo Vaccine 1'
        )
        print(f"   Created: {new_vaccine.vaccine_name} ({new_vaccine.vaccine_code})")

        # READ operations
        print("\n\n[READ] Retrieving records...")
        print("-" * 70)

        # Get area by code
        print("\n3. Retrieving the area we just created:")
        retrieved_area = crud.get_geographic_area('E99999999')
        if retrieved_area:
            print(f"   Found: {retrieved_area.area_name} ({retrieved_area.area_code})")
        else:
            print("   Area not found")

        # Get all vaccines
        print("\n4. Listing all vaccines in database:")
        all_vaccines = crud.get_all_vaccines()
        print(f"   Total vaccines: {len(all_vaccines)}")
        print("   Sample vaccines:")
        for vaccine in all_vaccines[:5]:  # Show first 5
            print(f"     - {vaccine.vaccine_name} ({vaccine.vaccine_code})")

        # Get vaccine by code
        print("\n5. Retrieving a specific vaccine (MMR1):")
        mmr1 = crud.get_vaccine('MMR1')
        if mmr1:
            print(f"   Found: {mmr1.vaccine_name} (ID: {mmr1.vaccine_id})")
        else:
            print("   Vaccine not found")

        # Get coverage records
        print("\n6. Querying coverage records for MMR1:")
        mmr1_records = crud.get_coverage_records(vaccine_code='MMR1')
        print(f"   Found {len(mmr1_records)} coverage records for MMR1")
        if mmr1_records:
            sample = mmr1_records[0]
            print(f"   Sample: Area {sample.area_code}, Coverage: {sample.coverage_percentage}%")

        # UPDATE operations
        print("\n\n[UPDATE] Modifying records...")
        print("-" * 70)

        # Update area name
        print("\n7. Updating the test area name:")
        updated_area = crud.update_geographic_area(
            'E99999999',
            area_name='Updated Demo Area'
        )
        if updated_area:
            print(f"   Updated: {updated_area.area_name}")
        else:
            print("   Update failed")

        # Update vaccine name
        print("\n8. Updating the test vaccine name:")
        updated_vaccine = crud.update_vaccine(
            'DEMO1',
            vaccine_name='Updated Demo Vaccine'
        )
        if updated_vaccine:
            print(f"   Updated: {updated_vaccine.vaccine_name}")
        else:
            print("   Update failed")

        # DELETE operations
        print("\n\n[DELETE] Removing records...")
        print("-" * 70)

        # Delete vaccine
        print("\n9. Deleting the test vaccine:")
        deleted_vaccine = crud.delete_vaccine('DEMO1')
        if deleted_vaccine:
            print("   Vaccine deleted successfully")
            # Verify deletion
            check = crud.get_vaccine('DEMO1')
            print(f"   Verification: Vaccine exists = {check is not None}")
        else:
            print("   Deletion failed")

        # Delete area
        print("\n10. Deleting the test area:")
        deleted_area = crud.delete_geographic_area('E99999999')
        if deleted_area:
            print("   Area deleted successfully")
            # Verify deletion
            check = crud.get_geographic_area('E99999999')
            print(f"   Verification: Area exists = {check is not None}")
        else:
            print("   Deletion failed")

        # Summary
        print("\n" + "=" * 70)
        print("CRUD DEMO COMPLETE!")
        print("=" * 70)
        print("\nAll CRUD operations executed successfully:")
        print("  - CREATE: Added new area and vaccine")
        print("  - READ: Retrieved individual records and lists")
        print("  - UPDATE: Modified area and vaccine names")
        print("  - DELETE: Removed test records")
        print()

        session.close()

    except FileNotFoundError:
        print("ERROR: Database file not found.")
        print("Please run create_database.py first to populate the database.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
