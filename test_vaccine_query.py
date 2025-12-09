"""Test the vaccine query logic."""

from src.database import get_session
from src.models import NationalCoverage, AgeCohort, FinancialYear, Vaccine

session = get_session()

cohort_name = '24 months'
year = 2024

cohort = session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
year_obj = session.query(FinancialYear).filter_by(year_start=year).first()

print(f"Cohort: {cohort.cohort_name} (ID: {cohort.cohort_id})")
print(f"Year: {year_obj.year_start} (ID: {year_obj.year_id})")

# This is what the code currently does
vaccine_ids_with_data = session.query(NationalCoverage.vaccine_id).filter_by(
    cohort_id=cohort.cohort_id,
    year_id=year_obj.year_id
).distinct().all()

print(f"\nVaccine IDs found: {[v_id[0] for v_id in vaccine_ids_with_data]}")

vaccine_ids = [v_id[0] for v_id in vaccine_ids_with_data]

# Get vaccine details for these IDs
vaccines = session.query(Vaccine).filter(
    Vaccine.vaccine_id.in_(vaccine_ids)
).order_by(Vaccine.vaccine_id).all()

print(f"\nVaccines found: {len(vaccines)}")
for v in vaccines:
    print(f"  - {v.vaccine_code}: {v.vaccine_name}")

session.close()
