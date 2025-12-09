from database_version_2.src.database import get_session
from database_version_2.src.models import LocalAuthorityCoverage, AgeCohort, FinancialYear, GeographicArea, Vaccine

session = get_session()

cohort = session.query(AgeCohort).filter_by(cohort_name='12 months').first()
year = session.query(FinancialYear).filter_by(year_start=2024).first()

print(f"Looking for cohort_id={cohort.cohort_id}, year_id={year.year_id}")

country_codes = ['E92000001', 'S92000003', 'W92000004', 'N92000002']

for code in country_codes:
    area = session.query(GeographicArea).filter_by(area_code=code).first()
    records = session.query(LocalAuthorityCoverage).filter_by(
        area_code=code,
        cohort_id=cohort.cohort_id,
        year_id=year.year_id
    ).all()

    print(f'\n{code} ({area.area_name}): {len(records)} records')

    if records:
        for r in records[:3]:
            vaccine = session.query(Vaccine).filter_by(vaccine_id=r.vaccine_id).first()
            print(f'  - {vaccine.vaccine_code}: {r.coverage_percentage}% (pop: {r.eligible_population})')
    else:
        print('  NO DATA FOUND')

session.close()
