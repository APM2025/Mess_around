"""Check national coverage data by cohort."""

from src.database import get_session
from src.models import NationalCoverage, AgeCohort, FinancialYear

session = get_session()

# Check available cohorts
cohorts = session.query(AgeCohort).all()
print('Available cohorts:')
for c in cohorts:
    print(f'  - {c.cohort_name} (ID: {c.cohort_id})')

# Check National Coverage data by cohort
print('\nNational Coverage data by cohort (year 2024):')
year_obj = session.query(FinancialYear).filter_by(year_start=2024).first()
if year_obj:
    for c in cohorts:
        count = session.query(NationalCoverage).filter_by(
            cohort_id=c.cohort_id,
            year_id=year_obj.year_id
        ).count()
        print(f'  {c.cohort_name}: {count} records')

        # Show sample data
        if count > 0:
            sample = session.query(NationalCoverage).filter_by(
                cohort_id=c.cohort_id,
                year_id=year_obj.year_id
            ).first()
            print(f'    Sample: area_code={sample.area_code}, vaccine_id={sample.vaccine_id}, coverage={sample.coverage_percentage}%')
else:
    print('Year 2024 not found!')

session.close()
