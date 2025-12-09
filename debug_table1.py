
import sys
import os
sys.path.append(os.getcwd())
from src.database_version_2.db_connection import get_db_session
from src.table_builder import TableBuilder

try:
    session = get_db_session()
    tb = TableBuilder(session)
    print("Attempting to get Table 1...")
    data = tb.get_table1_uk_by_country(cohort_name="24 months", year=2024)
    print("Success!")
    # print(data)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
