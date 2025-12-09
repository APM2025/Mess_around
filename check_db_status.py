"""Check database population status."""

from src.database import get_session
from src.models import *
from sqlalchemy import func

def main():
    session = get_session()

    print("=" * 60)
    print("DATABASE POPULATION STATUS")
    print("=" * 60)

    print("\nTable Counts:")
    print(f"  Geographic Areas: {session.query(GeographicArea).count()}")
    print(f"  Vaccines: {session.query(Vaccine).count()}")
    print(f"  Age Cohorts: {session.query(AgeCohort).count()}")
    print(f"  Financial Years: {session.query(FinancialYear).count()}")
    print(f"  National Coverage: {session.query(NationalCoverage).count()}")
    print(f"  Local Authority Coverage: {session.query(LocalAuthorityCoverage).count()}")
    print(f"  England Time Series: {session.query(EnglandTimeSeries).count()}")
    print(f"  Regional Time Series: {session.query(RegionalTimeSeries).count()}")
    print(f"  Special Programs: {session.query(SpecialProgram).count()}")

    print("\n" + "=" * 60)
    print("GEOGRAPHIC AREA BREAKDOWN")
    print("=" * 60)

    area_types = session.query(
        GeographicArea.area_type,
        func.count(GeographicArea.area_code)
    ).group_by(GeographicArea.area_type).all()

    for area_type, count in area_types:
        print(f"  {area_type}: {count}")

    print("\n" + "=" * 60)
    print("SAMPLE AREAS (First 10)")
    print("=" * 60)

    sample_areas = session.query(GeographicArea).limit(10).all()
    for area in sample_areas:
        print(f"  {area.area_code} | {area.area_type:10} | {area.area_name}")

    print("\n" + "=" * 60)
    print("VACCINES")
    print("=" * 60)

    vaccines = session.query(Vaccine).all()
    for v in vaccines:
        print(f"  {v.vaccine_code:20} | {v.vaccine_name}")

if __name__ == '__main__':
    main()
