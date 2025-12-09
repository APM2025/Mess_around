"""
Module to rebuild original ODS table views from the database.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database_version_2.src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, RegionalTimeSeries
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

        # Get countries (UK-level and country-level areas)
        countries = self.session.query(GeographicArea).filter(
            GeographicArea.area_type == 'country'
        ).order_by(GeographicArea.area_code).all()

        # Get vaccines for this cohort - for 12 months in specific order
        target_vaccines = ['DTaP_IPV_Hib_HepB', 'PCV1', 'Rota', 'MenB']

        # Get vaccines and maintain order
        vaccine_map = {}
        all_vaccines = self.session.query(Vaccine).filter(
            Vaccine.vaccine_code.in_(target_vaccines)
        ).all()

        for v in all_vaccines:
            vaccine_map[v.vaccine_code] = v

        # Create ordered list
        vaccines = [vaccine_map[code] for code in target_vaccines if code in vaccine_map]

        data = []

        # Create UK summary row by aggregating country data (with ordered columns)
        uk_row = {}
        uk_row['geographic_area'] = 'United Kingdom'
        uk_row['note'] = '[note 23]'
        uk_row['number_aged_12_months'] = 0

        uk_coverage_sums = {}
        uk_coverage_counts = {}

        for vaccine in vaccines:
            uk_coverage_sums[vaccine.vaccine_id] = 0
            uk_coverage_counts[vaccine.vaccine_id] = 0

        for area in countries:
            # Create row with columns in correct order
            row = {}
            row['geographic_area'] = area.area_name
            row['note'] = '[note 23]' if area.area_name == 'England' or area.area_name == 'United Kingdom' else '[z]'
            row['number_aged_12_months'] = None

            # Get coverage records
            coverage_records = self.session.query(LocalAuthorityCoverage).filter_by(
                area_code=area.area_code,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id
            ).all()

            coverage_map = {rec.vaccine_id: rec for rec in coverage_records}

            # Set eligible population
            if coverage_records:
                row['number_aged_12_months'] = coverage_records[0].eligible_population
                uk_row['number_aged_12_months'] += coverage_records[0].eligible_population or 0

            # Add coverage for each vaccine - store temporarily
            vaccine_coverage = {}
            for vaccine in vaccines:
                col_name = f'coverage_at_12_months_{vaccine.vaccine_code}'
                if vaccine.vaccine_id in coverage_map:
                    coverage_val = coverage_map[vaccine.vaccine_id].coverage_percentage
                    vaccine_coverage[col_name] = coverage_val

                    # Aggregate for UK
                    if coverage_val is not None:
                        uk_coverage_sums[vaccine.vaccine_id] += coverage_val
                        uk_coverage_counts[vaccine.vaccine_id] += 1
                else:
                    vaccine_coverage[col_name] = None

            # Add vaccine columns in correct order
            for vaccine in vaccines:
                col_name = f'coverage_at_12_months_{vaccine.vaccine_code}'
                row[col_name] = vaccine_coverage[col_name]

            data.append(row)

        # Calculate UK averages - add vaccine columns to uk_row
        for vaccine in vaccines:
            col_name = f'coverage_at_12_months_{vaccine.vaccine_code}'
            if uk_coverage_counts[vaccine.vaccine_id] > 0:
                uk_row[col_name] = uk_coverage_sums[vaccine.vaccine_id] / uk_coverage_counts[vaccine.vaccine_id]
            else:
                uk_row[col_name] = None

        # Reorder UK row to match column order (geographic_area, note, number, then vaccines)
        uk_row_ordered = {}
        uk_row_ordered['geographic_area'] = uk_row['geographic_area']
        uk_row_ordered['note'] = uk_row['note']
        uk_row_ordered['number_aged_12_months'] = uk_row['number_aged_12_months']
        for vaccine in vaccines:
            col_name = f'coverage_at_12_months_{vaccine.vaccine_code}'
            uk_row_ordered[col_name] = uk_row[col_name]

        # Insert UK row at the beginning
        data.insert(0, uk_row_ordered)

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

        # Get all UTLAs with their coverage data
        areas = self.session.query(GeographicArea).filter_by(area_type=area_type).all()

        # Get all vaccines for this cohort
        vaccines = self.session.query(Vaccine).all()
        vaccine_codes = [v.vaccine_code for v in vaccines]

        results = []

        for area in areas:
            row = {
                'code': area.area_code,
                'local_authority': area.area_name,
                'region_name': area.parent_region_code or '',
                'ods_code': area.ods_code or '',
                'note': '',  # Notes can be added if needed
            }

            # Get coverage for each vaccine
            coverage_records = self.session.query(LocalAuthorityCoverage).filter_by(
                area_code=area.area_code,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id
            ).all()

            # Create a map of vaccine_id to coverage
            coverage_map = {rec.vaccine_id: rec for rec in coverage_records}

            # Add population count (use first record's eligible_population)
            if coverage_records:
                row['eligible_population'] = coverage_records[0].eligible_population or 0
            else:
                row['eligible_population'] = 0

            # Add coverage for each vaccine
            for vaccine in vaccines:
                col_name = f'coverage_{vaccine.vaccine_code}'
                if vaccine.vaccine_id in coverage_map:
                    row[col_name] = coverage_map[vaccine.vaccine_id].coverage_percentage
                else:
                    row[col_name] = None

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
                    'vaccinated_count': record.vaccinated_count,
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
