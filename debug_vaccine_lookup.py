from pathlib import Path
from backend_code.database_src.database import create_test_session
from backend_code.database_src.load_reference_data import load_all_reference_data
from backend_code.database_src.models import Vaccine

p = Path('test_debug.db')
if p.exists():
    p.unlink()

s = create_test_session(p)
load_all_reference_data(s)

print('=== ALL VACCINES IN DB ===')
for v in s.query(Vaccine).all():
    print(f'  ID {v.vaccine_id}: {v.vaccine_code} - {v.vaccine_name}')

print('\n=== TESTING LOOKUPS ===')
dtap = s.query(Vaccine).filter(Vaccine.vaccine_code.contains('DTaP')).first()
print(f'DTaP lookup result: {dtap.vaccine_code if dtap else "NOT FOUND"}')
if dtap:
    print(f'  vaccine_id: {dtap.vaccine_id}')

mmr = s.query(Vaccine).filter(Vaccine.vaccine_code.contains('MMR')).first()
print(f'MMR lookup result: {mmr.vaccine_code if mmr else "NOT FOUND"}')
if mmr:
    print(f'  vaccine_id: {mmr.vaccine_id}')

print(f'\n=== RESULT ===')
print(f'Both lookups find different vaccines? {dtap.vaccine_id != mmr.vaccine_id if (dtap and mmr) else False}')

s.close()
