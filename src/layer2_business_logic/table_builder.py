"""
Module to rebuild original ODS table views from the database.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from src.layer1_database.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    NationalCoverage, LocalAuthorityCoverage, RegionalTimeSeries, SpecialProgram
)


class TableBuilder:
    """Rebuilds original ODS table format from database."""

    def __init__(self, session: Session):
        """
        Initialize table builder.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def get_table1_uk_by_country(self, cohort_name: str = '12 months', year: int = 2024) -> Dict[str, Any]:
        """
        Table 1: Completed primary immunisations in children aged 12 months in the UK, by country.

        Args:
            cohort_name: Age cohort (default: '12 months')
            year: Year (default: 2024)

        Returns:
            Dictionary with table metadata and data
        """
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()

        if not cohort or not year_obj:
            return {
                'title': f'Table 1. Completed primary immunisations in children aged {cohort_name} in the UK, by country',
                'notes': [],
                'data': []
            }

        # Get countries (UK-level and country-level areas) by area_code for correct order
        country_codes = [
            ('K02000001', 'United Kingdom'),
            ('E92000001', 'England'),
            ('S92000003', 'Scotland'),
            ('W92000004', 'Wales'),
            ('N92000002', 'Northern Ireland')
        ]
        countries = []
        print("[DEBUG] Checking country codes in DB:")
        for code, name in country_codes:
            area = self.session.query(GeographicArea).filter_by(area_code=code).first()
            if area:
                print(f"  Found: {name} (area_code={code})")
                countries.append(area)
            else:
                print(f"  MISSING: {name} (area_code={code})")

        # Get ALL vaccines to ensure columns appear even if no data (for CRUD demo)
        vaccines = self.session.query(Vaccine).order_by(Vaccine.vaccine_id).all()


        data = []

        data = []
        for area in countries:
            # Use display name from mapping for UK and countries
            display_name = None
            for code, name in country_codes:
                if area.area_code == code:
                    display_name = name
                    break
            if not display_name:
                display_name = area.area_name

            # Get coverage records for this area
            coverage_records = self.session.query(NationalCoverage).filter_by(
                area_code=area.area_code,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id
            ).all()

            coverage_map = {rec.vaccine_id: rec for rec in coverage_records}

            # Build row in EXACT column order required
            row = {}
            row['code'] = area.area_code  # Required for CRUD
            row['geographic_area'] = display_name
            row['note'] = '[note 23]' if display_name == 'England' or display_name == 'United Kingdom' else '[z]'

            # Column name uses selected cohort name
            cohort_label = cohort_name.replace(' ', '_')
            if coverage_records:
                row[f'number_aged_{cohort_label}'] = coverage_records[0].eligible_population
            else:
                row[f'number_aged_{cohort_label}'] = None

            # Add coverage columns for each vaccine
            for vaccine in vaccines:
                col_name = f'coverage_at_{cohort_label}_{vaccine.vaccine_code}'
                vac_col_name = f'vaccinated_at_{cohort_label}_{vaccine.vaccine_code}'
                
                if vaccine.vaccine_id in coverage_map:
                    row[col_name] = coverage_map[vaccine.vaccine_id].coverage_percentage
                    row[vac_col_name] = coverage_map[vaccine.vaccine_id].vaccinated_count
                else:
                    row[col_name] = None
                    row[vac_col_name] = None

            data.append(row)

        return {
            'title': f'Table 1. Completed primary immunisations in children aged {cohort_name} in the UK, by country',
            'notes': [
                '[z] not applicable',
                '[note 23] Please note that system changes in 14 UTLAs in London earlier this year...'
            ],
            'data': data,
            'cohort': cohort_name,
            'year': year
        }

    def get_utla_table(
        self,
        cohort_name: str = '24 months',
        year: int = 2024,
        area_type: str = 'utla'
    ) -> List[Dict[str, Any]]:
        """
        Get UTLA coverage table in original ODS format.
        Column names are always for "12 months" cohort but data varies by selected cohort.

        Args:
            cohort_name: Age cohort ('24 months', '12 months', '5 years')
            year: Year to fetch data for
            area_type: Type of area (default: 'utla')

        Returns:
            List of dictionaries with table data
        """
        # Get cohort and year IDs
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()

        if not cohort or not year_obj:
            return []

        # Get all UTLAs sorted by name
        areas = self.session.query(GeographicArea).filter_by(area_type=area_type).order_by(GeographicArea.area_name).all()

        # Get ALL vaccines to ensure columns appear even if no data (for CRUD demo)
        vaccines = self.session.query(Vaccine).order_by(Vaccine.vaccine_id).all()

        results = []

        for area in areas:
            # Get coverage records for this area and selected cohort
            coverage_records = self.session.query(LocalAuthorityCoverage).filter_by(
                area_code=area.area_code,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id
            ).all()

            # Create a map of vaccine_id to coverage record
            coverage_map = {rec.vaccine_id: rec for rec in coverage_records}

            row = {}
            row['code'] = area.area_code
            row['local_authority'] = area.area_name
            if area.parent_region:
                row['region_name'] = area.parent_region.area_name
            else:
                row['region_name'] = area.parent_region_code or ''
            row['ods_code'] = area.ods_code or ''
            
            # Add notes for special cases
            note = ''
            if 'City of London' in area.area_name:
                note = '[note 18]'
            elif 'Isles of Scilly' in area.area_name:
                note = '[note 19]'
            row['note'] = note

            # Add eligible population (column name uses selected cohort)
            cohort_label = cohort_name.replace(' ', '_')
            if coverage_records:
                row[f'number_aged_{cohort_label}'] = coverage_records[0].eligible_population or 0
            else:
                row[f'number_aged_{cohort_label}'] = 0

            # Add vaccine columns in specific order: vaccinated count, then coverage %
            for vaccine in vaccines:
                # Vaccinated count column
                vaccinated_col = f'vaccinated_at_{cohort_label}_{vaccine.vaccine_code}'
                coverage_col = f'coverage_at_{cohort_label}_{vaccine.vaccine_code}'

                if vaccine.vaccine_id in coverage_map:
                    record = coverage_map[vaccine.vaccine_id]
                    # Use stored vaccinated_count if available, otherwise calculate from coverage
                    if record.vaccinated_count is not None:
                        row[vaccinated_col] = record.vaccinated_count
                    elif record.coverage_percentage is not None and record.eligible_population:
                        # Calculate: vaccinated = (coverage% / 100) * eligible_population
                        row[vaccinated_col] = int((record.coverage_percentage / 100.0) * record.eligible_population)
                    else:
                        row[vaccinated_col] = None
                    row[coverage_col] = record.coverage_percentage
                else:
                    row[vaccinated_col] = None
                    row[coverage_col] = None

            results.append(row)

        return results

    def get_regional_table(
        self,
        cohort_name: str = '24 months',
        area_type: str = 'region'
    ) -> List[Dict[str, Any]]:
        """
        Get regional coverage table with time series.

        Args:
            cohort_name: Age cohort
            area_type: Type of area (default: 'region')

        Returns:
            List of dictionaries with regional time series data
        """
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        if not cohort:
            return []

        # Get all regions
        areas = self.session.query(GeographicArea).filter_by(area_type=area_type).all()

        results = []

        for area in areas:
            # Get time series data for this area
            time_series = self.session.query(RegionalTimeSeries).filter_by(
                area_code=area.area_code,
                cohort_id=cohort.cohort_id
            ).order_by(RegionalTimeSeries.year_id).all()

            for record in time_series:
                year = self.session.query(FinancialYear).filter_by(year_id=record.year_id).first()
                vaccine = self.session.query(Vaccine).filter_by(vaccine_id=record.vaccine_id).first()

                row = {
                    'code': area.area_code,
                    'area_name': area.area_name,
                    'year': year.year_start if year else None,
                    'vaccine_code': vaccine.vaccine_code if vaccine else None,
                    'vaccine_name': vaccine.vaccine_name if vaccine else None,
                    'coverage_percentage': record.coverage_percentage,
                    'eligible_population': record.eligible_population
                }

                results.append(row)

        return results

    def get_england_summary(
        self,
        cohort_name: str = '24 months',
        year: int = 2024
    ) -> Dict[str, Any]:
        """
        Get England-level summary statistics.

        Args:
            cohort_name: Age cohort
            year: Year

        Returns:
            Dictionary with summary statistics
        """
        cohort = self.session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()

        if not cohort or not year_obj:
            return {}

        # Get England area (typically E92000001)
        england = self.session.query(GeographicArea).filter(
            GeographicArea.area_code.like('E92000001')
        ).first()

        if not england:
            return {}

        # Get all coverage records for England
        coverage_records = self.session.query(LocalAuthorityCoverage).filter_by(
            area_code=england.area_code,
            cohort_id=cohort.cohort_id,
            year_id=year_obj.year_id
        ).all()

        vaccines = self.session.query(Vaccine).all()
        vaccine_map = {v.vaccine_id: v for v in vaccines}

        result = {
            'code': england.area_code,
            'area_name': england.area_name,
            'cohort': cohort_name,
            'year': year,
            'vaccines': []
        }

        for record in coverage_records:
            vaccine = vaccine_map.get(record.vaccine_id)
            if vaccine:
                result['vaccines'].append({
                    'vaccine_code': vaccine.vaccine_code,
                    'vaccine_name': vaccine.vaccine_name,
                    'coverage_percentage': record.coverage_percentage,
                    'eligible_population': record.eligible_population
                })

        return result

    def get_hepb_table(self, year: int = 2024) -> Dict[str, Any]:
        """
        Table 7: Neonatal Hepatitis B coverage by UTLA.

        Args:
            year: Year to fetch data for

        Returns:
            Dictionary with table metadata and data
        """
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()

        if not year_obj:
            return {
                'title': 'Table 7. Neonatal hepatitis B coverage in eligible children by UTLA',
                'notes': [],
                'data': []
            }

        # Get all UTLAs
        areas = self.session.query(GeographicArea).filter_by(area_type='utla').order_by(GeographicArea.area_name).all()

        # Get HepB data for 12 months and 24 months cohorts
        cohort_12m = self.session.query(AgeCohort).filter_by(cohort_name='12 months').first()
        cohort_24m = self.session.query(AgeCohort).filter_by(cohort_name='24 months').first()

        data = []
        for area in areas:
            row = {
                'local_authority': area.area_name,
                'ods_code': area.ods_code or '',
                'note': ''
            }

            # Get HepB coverage for 12 months
            if cohort_12m:
                hepb_12m = self.session.query(SpecialProgram).filter_by(
                    area_code=area.area_code,
                    program_type='HepB',
                    cohort_id=cohort_12m.cohort_id,
                    year_id=year_obj.year_id
                ).first()

                if hepb_12m:
                    row['eligible_12m'] = hepb_12m.eligible_population
                    row['vaccinated_12m'] = hepb_12m.vaccinated_count
                    row['coverage_12m'] = hepb_12m.coverage_percentage or hepb_12m.coverage_range
                else:
                    row['eligible_12m'] = None
                    row['vaccinated_12m'] = None
                    row['coverage_12m'] = None

            # Get HepB coverage for 24 months
            if cohort_24m:
                hepb_24m = self.session.query(SpecialProgram).filter_by(
                    area_code=area.area_code,
                    program_type='HepB',
                    cohort_id=cohort_24m.cohort_id,
                    year_id=year_obj.year_id
                ).first()

                if hepb_24m:
                    row['eligible_24m'] = hepb_24m.eligible_population
                    row['vaccinated_24m'] = hepb_24m.vaccinated_count
                    row['coverage_24m'] = hepb_24m.coverage_percentage or hepb_24m.coverage_range
                else:
                    row['eligible_24m'] = None
                    row['vaccinated_24m'] = None
                    row['coverage_24m'] = None

            data.append(row)

        return {
            'title': 'Table 7. Neonatal hepatitis B coverage in eligible children aged 12 and 24 months by UTLA',
            'notes': [
                '[c] Some figures have been suppressed due to potential disclosure issues associated with small numbers.',
                '[z] not applicable',
                '[note 18] City of London is included in Hackney.',
                '[note 19] Isles of Scilly is included in Cornwall.'
            ],
            'data': data,
            'year': year
        }

    def get_bcg_table(self, year: int = 2024) -> Dict[str, Any]:
        """
        Table 8: BCG vaccine coverage by UTLA.

        Args:
            year: Year to fetch data for

        Returns:
            Dictionary with table metadata and data
        """
        year_obj = self.session.query(FinancialYear).filter_by(year_start=year).first()

        if not year_obj:
            return {
                'title': 'Table 8. BCG vaccine coverage in eligible children by UTLA',
                'notes': [],
                'data': []
            }

        # Get all UTLAs
        areas = self.session.query(GeographicArea).filter_by(area_type='utla').order_by(GeographicArea.area_name).all()

        # BCG has special cohorts - check what's in the database
        # Typically 3 months and 12 months for BCG
        data = []
        for area in areas:
            row = {
                'local_authority': area.area_name,
                'ods_code': area.ods_code or '',
                'note': ''
            }

            # Get all BCG records for this area and year
            bcg_records = self.session.query(SpecialProgram).filter_by(
                area_code=area.area_code,
                program_type='BCG',
                year_id=year_obj.year_id
            ).all()

            # Group by cohort
            for record in bcg_records:
                cohort = self.session.query(AgeCohort).filter_by(cohort_id=record.cohort_id).first()
                if cohort:
                    cohort_label = cohort.cohort_name.replace(' ', '_')
                    row[f'eligible_{cohort_label}'] = record.eligible_population
                    row[f'vaccinated_{cohort_label}'] = record.vaccinated_count
                    row[f'coverage_{cohort_label}'] = record.coverage_percentage or record.coverage_range

            data.append(row)

        return {
            'title': 'Table 8. BCG vaccine coverage in eligible children by UTLA',
            'notes': [
                '[c] Some figures have been suppressed due to potential disclosure issues associated with small numbers.',
                '[z] not applicable',
                '[note 18] City of London is included in Hackney.',
                '[note 19] Isles of Scilly is included in Cornwall.'
            ],
            'data': data,
            'year': year
        }
