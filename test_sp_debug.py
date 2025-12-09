from pathlib import Path
from backend_code.database_src.database import create_test_session
from backend_code.database_src.load_reference_data import load_all_reference_data
from backend_code.database_src.load_special_programs import load_special_programs_from_csv
from backend_code.database_src.models import SpecialProgram

p = Path('test_sp.db')
if p.exists():
    p.unlink()

s = create_test_session(p)
load_all_reference_data(s)

csv_path = Path('data/csv_data/cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv')
try:
    load_special_programs_from_csv(csv_path, s)
    
    records = s.query(SpecialProgram).all()
    print(f"\n=== RESULTS ===")
    print(f"Total records: {len(records)}")
    if records:
        print(f"Sample record: {records[0].__dict__}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

s.close()
