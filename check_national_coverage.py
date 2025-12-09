from database_version_2.src.database import get_session
from database_version_2.src.models import NationalCoverage, AgeCohort, FinancialYear, Vaccine

session = get_session()

print("=== Checking NationalCoverage Table ===\n")

# Check total records
total = session.query(NationalCoverage).count()
print(f"Total NationalCoverage records: {total}\n")

# Check for 12 months cohort
cohort = session.query(AgeCohort).filter_by(cohort_name='12 months').first()
print(f"Cohort ID for '12 months': {cohort.cohort_id if cohort else 'NOT FOUND'}\n")

if cohort:
    records_12m = session.query(NationalCoverage).filter_by(cohort_id=cohort.cohort_id).all()
    print(f"Records for 12 months cohort: {len(records_12m)}\n")

    if records_12m:
        print("Sample records:")
        countries = {}
        for r in records_12m[:20]:
            year = session.query(FinancialYear).filter_by(year_id=r.year_id).first()
            vaccine = session.query(Vaccine).filter_by(vaccine_id=r.vaccine_id).first()

            country = r.country
            if country not in countries:
                countries[country] = []
            countries[country].append({
                'year': year.year_start if year else '?',
                'vaccine': vaccine.vaccine_code if vaccine else '?',
                'coverage': r.coverage_percentage,
                'population': r.eligible_population
            })

        for country, data in list(countries.items())[:5]:
            print(f"\n{country}:")
            for d in data[:3]:
                print(f"  {d['year']}: {d['vaccine']} = {d['coverage']}% (pop: {d['population']})")

session.close()
