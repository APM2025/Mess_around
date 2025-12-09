from pathlib import Path
from backend_code.database_src.database import create_test_session
from backend_code.database_src.load_reference_data import load_all_reference_data
from backend_code.database_src.load_regional_time_series import load_all_regional_time_series
from backend_code.database_src.models import RegionalTimeSeries, Vaccine

p = Path('test_regional_debug.db')
if p.exists():
    p.unlink()

s = create_test_session(p)
load_all_reference_data(s)
load_all_regional_time_series(Path('data/csv_data'), s)

print('\n=== FINAL DATABASE CHECK ===')
vaccines = s.query(RegionalTimeSeries.vaccine_id, Vaccine.vaccine_code).join(Vaccine).distinct().all()
print(f'Unique vaccines in table: {len(vaccines)}')

for vid, vcode in vaccines:
    count = s.query(RegionalTimeSeries).filter_by(vaccine_id=vid).count()
    print(f'  {vcode} (ID {vid}): {count} records')

total = s.query(RegionalTimeSeries).count()
print(f'\nTotal records: {total}')

s.close()
