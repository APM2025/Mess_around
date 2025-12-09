"""Check what's in the database"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database_version_2.src.database import get_session
from database_version_2.src.models import Vaccine, AgeCohort, LocalAuthorityCoverage

session = get_session()

print("=" * 60)
print("VACCINES IN DATABASE:")
print("=" * 60)
vaccines = session.query(Vaccine).all()
for v in vaccines:
    print(f"{v.vaccine_code:20s} | {v.vaccine_name}")

print("\n" + "=" * 60)
print("AGE COHORTS IN DATABASE:")
print("=" * 60)
cohorts = session.query(AgeCohort).all()
for c in cohorts:
    print(f"{c.cohort_name:15s} | {c.age_months} months")

print("\n" + "=" * 60)
print("SAMPLE LOCAL AUTHORITY COVERAGE (first 5):")
print("=" * 60)
records = session.query(LocalAuthorityCoverage).limit(5).all()
for r in records:
    print(f"Vaccine ID: {r.vaccine_id}, Cohort ID: {r.cohort_id}, Coverage: {r.coverage_percentage}%")

session.close()
