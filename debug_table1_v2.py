
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from src.database import get_session
from src.table_builder import TableBuilder
from src.models import GeographicArea, FinancialYear, AgeCohort, Vaccine

try:
    session = get_session()
    print("Session created.")
    
    # Check if we have basic data
    countries = session.query(GeographicArea).filter_by(area_type='Country').all()
    print(f"Found {len(countries)} countries.")
    
    tb = TableBuilder(session)
    print("Attempting to get Table 1...")
    data = tb.get_table1_uk_by_country(cohort_name="24 months", year=2024)
    print("Success! Data length:", len(data['data']))
    
    # Print the first row keys to check structure
    if data['data']:
        print("Keys in first row:", data['data'][0].keys())
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
