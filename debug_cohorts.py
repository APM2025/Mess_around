"""Debug script to check vaccine data for different cohorts."""

from src.database import get_session
from src.models import NationalCoverage, AgeCohort, FinancialYear, Vaccine

session = get_session()

year_obj = session.query(FinancialYear).filter_by(year_start=2024).first()
print(f'Year ID for 2024: {year_obj.year_id if year_obj else None}')

for cohort_name in ['12 months', '24 months', '5 years']:
    cohort = session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
    if not cohort:
        print(f'\n{cohort_name}: COHORT NOT FOUND')
        continue

    print(f'\n{cohort_name} (cohort_id={cohort.cohort_id}):')

    # Get all records for this cohort
    records = session.query(NationalCoverage).filter_by(
        cohort_id=cohort.cohort_id,
        year_id=year_obj.year_id
    ).all()

    print(f'  Total records: {len(records)}')

    # Get unique vaccine IDs
    vaccine_ids = set(r.vaccine_id for r in records)
    print(f'  Unique vaccine IDs: {vaccine_ids}')

    # Get vaccine details
    for vid in vaccine_ids:
        v = session.query(Vaccine).filter_by(vaccine_id=vid).first()
        if v:
            print(f'    - vaccine_id={vid}: {v.vaccine_code} ({v.vaccine_name})')

session.close()
