"""Check which vaccines are available for each cohort."""

from src.database import get_session
from src.models import NationalCoverage, AgeCohort, FinancialYear, Vaccine

session = get_session()

year_obj = session.query(FinancialYear).filter_by(year_start=2024).first()

for cohort_name in ['12 months', '24 months', '5 years']:
    cohort = session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()

    print(f'\n{cohort_name} cohort:')

    # Get all vaccines with data for this cohort
    records = session.query(NationalCoverage).filter_by(
        cohort_id=cohort.cohort_id,
        year_id=year_obj.year_id,
        area_code='K02000001'  # UK
    ).all()

    print(f'  Found {len(records)} vaccine records for UK')

    for rec in records:
        vaccine = session.query(Vaccine).filter_by(vaccine_id=rec.vaccine_id).first()
        if vaccine:
            print(f'    - {vaccine.vaccine_code}: {rec.coverage_percentage}%')

session.close()
