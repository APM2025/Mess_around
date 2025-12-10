"""
Filtering and analysis for vaccination coverage data.
"""

import statistics
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from src.layer1_database.models import (
    LocalAuthorityCoverage,
    Vaccine,
    GeographicArea,
    AgeCohort,
    EnglandTimeSeries,
    FinancialYear
)


class VaccinationAnalyzer:
    """Analyzes vaccination coverage data."""

    def __init__(self, session: Session):
        self.session = session

    def filter_data(
        self,
        vaccine_code: Optional[str] = None,
        area_type: str = 'utla',
        cohort_name: str = '24_months'
    ) -> List[Dict[str, Any]]:
        """
        Filter vaccination coverage data.

        Args:
            vaccine_code: Vaccine code to filter by (e.g., 'MMR1')
            area_type: Type of area ('utla', 'country', 'region')
            cohort_name: Age cohort (e.g., '24_months')

        Returns:
            List of dicts with area_name, coverage, vaccine_code, vaccine_name
        """
        # Build query with JOINs
        query = self.session.query(
            GeographicArea.area_name,
            LocalAuthorityCoverage.coverage_percentage,
            Vaccine.vaccine_code,
            Vaccine.vaccine_name
        ).join(
            LocalAuthorityCoverage,
            GeographicArea.area_code == LocalAuthorityCoverage.area_code
        ).join(
            Vaccine,
            LocalAuthorityCoverage.vaccine_id == Vaccine.vaccine_id
        ).join(
            AgeCohort,
            LocalAuthorityCoverage.cohort_id == AgeCohort.cohort_id
        )

        # Apply filters
        query = query.filter(GeographicArea.area_type == area_type)
        query = query.filter(AgeCohort.cohort_name == cohort_name)

        if vaccine_code:
            query = query.filter(Vaccine.vaccine_code == vaccine_code)

        # Execute query
        results = query.all()

        # Convert to list of dicts
        data = []
        for row in results:
            if row[1] is not None:  # Skip NULL coverage
                data.append({
                    'area_name': row[0],
                    'coverage': row[1],
                    'vaccine_code': row[2],
                    'vaccine_name': row[3]
                })

        return data

    def get_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics.

        Args:
            data: List of coverage records from filter_data()

        Returns:
            Dict with mean, min, max, count
        """
        if not data:
            return {
                'count': 0,
                'mean': None,
                'min': None,
                'max': None
            }

        # Extract coverage values
        coverages = [d['coverage'] for d in data]

        return {
            'count': len(coverages),
            'mean': round(statistics.mean(coverages), 1),
            'min': round(min(coverages), 1),
            'max': round(max(coverages), 1)
        }

    def get_top_areas(
        self,
        vaccine_code: str,
        n: int = 10,
        cohort_name: str = '24_months'
    ) -> List[Dict[str, Any]]:
        """
        Get top N performing areas.

        Args:
            vaccine_code: Vaccine to filter by
            n: Number of top areas to return
            cohort_name: Age cohort

        Returns:
            List of top N areas, sorted by coverage descending
        """
        # Get all data for this vaccine
        data = self.filter_data(
            vaccine_code=vaccine_code,
            cohort_name=cohort_name
        )

        # Sort by coverage descending
        sorted_data = sorted(
            data,
            key=lambda x: x['coverage'],
            reverse=True
        )

        # Return top N
        return sorted_data[:n]

    def get_trend(
        self,
        vaccine_code: str,
        cohort_name: str = '24_months'
    ) -> List[Dict[str, Any]]:
        """
        Get coverage trend over time for England.

        Args:
            vaccine_code: Vaccine to analyze
            cohort_name: Age cohort

        Returns:
            List of {year, coverage} dicts, ordered chronologically
        """
        # Get vaccine and cohort
        vaccine = self.session.query(Vaccine).filter_by(
            vaccine_code=vaccine_code
        ).first()

        cohort = self.session.query(AgeCohort).filter_by(
            cohort_name=cohort_name
        ).first()

        if not vaccine or not cohort:
            return []

        # Query time series data
        query = self.session.query(
            FinancialYear.year_label,
            EnglandTimeSeries.coverage_percentage
        ).join(
            EnglandTimeSeries,
            FinancialYear.year_id == EnglandTimeSeries.year_id
        ).filter(
            EnglandTimeSeries.vaccine_id == vaccine.vaccine_id,
            EnglandTimeSeries.cohort_id == cohort.cohort_id
        ).order_by(FinancialYear.year_start)

        results = query.all()

        # Convert to list of dicts
        return [
            {'year': row[0], 'coverage': row[1]}
            for row in results
            if row[1] is not None
        ]

    def filter_table_data(
        self,
        table_data: List[Dict[str, Any]],
        filters: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Filter table data by multiple column criteria.

        This method demonstrates backend filtering capabilities for assessment.
        It applies filters to pre-built table data from table_builder.

        Args:
            table_data: List of row dictionaries from table_builder
            filters: Dict mapping column names to lists of allowed values
                    e.g., {'geographic_area': ['England', 'Scotland'],
                           'region_name': ['London', 'South East']}

        Returns:
            Filtered list of row dictionaries

        Example:
            >>> filters = {'geographic_area': ['England', 'Wales']}
            >>> filtered = analyzer.filter_table_data(table_data, filters)
        """
        if not filters:
            return table_data

        filtered_rows = []

        for row in table_data:
            # Check if row matches ALL filter criteria (AND logic)
            matches = True

            for column, allowed_values in filters.items():
                if not allowed_values:  # Skip empty filters
                    continue

                # Get cell value, handle None/missing columns
                cell_value = row.get(column)

                # Convert to string for comparison
                if cell_value is not None:
                    if isinstance(cell_value, (int, float)):
                        cell_str = str(cell_value)
                    else:
                        cell_str = str(cell_value)
                else:
                    cell_str = ''

                # Check if cell value is in allowed values
                if cell_str not in allowed_values:
                    matches = False
                    break

            if matches:
                filtered_rows.append(row)

        return filtered_rows

    @staticmethod
    def classify_coverage(coverage_percentage: Optional[float]) -> str:
        """
        Classify coverage percentage into performance categories.

        Classification thresholds:
        - >= 95%: 'good' (green)
        - 85-95%: 'warning' (orange/amber)
        - < 85%: 'low' (red)
        - None/null: 'unknown' (no data)

        Args:
            coverage_percentage: Coverage value (0-100)

        Returns:
            Classification string: 'good', 'warning', 'low', or 'unknown'

        Example:
            >>> VaccinationAnalyzer.classify_coverage(96.5)
            'good'
            >>> VaccinationAnalyzer.classify_coverage(88.0)
            'warning'
            >>> VaccinationAnalyzer.classify_coverage(82.3)
            'low'
        """
        if coverage_percentage is None:
            return 'unknown'

        if coverage_percentage >= 95.0:
            return 'good'
        elif coverage_percentage >= 85.0:
            return 'warning'
        else:
            return 'low'

    def calculate_table_statistics(
        self,
        table_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics for table data.

        Computes aggregate statistics (mean, min, max, count) for all
        coverage columns in the table data.

        Args:
            table_data: List of row dictionaries from table_builder

        Returns:
            Dictionary containing:
            - row_count: Total number of rows
            - vaccine_stats: Dict mapping vaccine names to their statistics
                            (avg, min, max, count)

        Example:
            >>> stats = analyzer.calculate_table_statistics(table_data)
            >>> stats['vaccine_stats']['DTaP/IPV/Hib/HepB']
            {'avg': 92.5, 'min': 85.0, 'max': 98.0, 'count': 150}
        """
        if not table_data or len(table_data) == 0:
            return {
                'row_count': 0,
                'vaccine_stats': {}
            }

        stats = {
            'row_count': len(table_data),
            'vaccine_stats': {}
        }

        # Get all coverage columns from first row
        first_row = table_data[0]
        coverage_columns = [col for col in first_row.keys() if col.startswith('coverage_at_')]

        # Calculate statistics for each coverage column
        for col in coverage_columns:
            # Extract vaccine name from column name
            # e.g., "coverage_at_12_months_DTaP_IPV_Hib_HepB" -> "DTaP/IPV/Hib/HepB"
            # or "coverage_at_24_months_MMR1" -> "MMR1"
            vaccine_name = col

            # Remove coverage_at_ prefix
            vaccine_name = vaccine_name.replace('coverage_at_', '')

            # Remove cohort prefixes (12_months_, 24_months_, 5_years_)
            vaccine_name = vaccine_name.replace('12_months_', '')
            vaccine_name = vaccine_name.replace('24_months_', '')
            vaccine_name = vaccine_name.replace('5_years_', '')

            # Convert underscores to slashes for display
            vaccine_name = vaccine_name.replace('_', '/')

            # Collect all non-null values for this column
            values = []
            for row in table_data:
                val = row.get(col)
                if val is not None and not (isinstance(val, float) and val != val):  # Check for NaN
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        pass

            # Calculate statistics if we have values
            if values:
                stats['vaccine_stats'][vaccine_name] = {
                    'avg': round(statistics.mean(values), 1),
                    'min': round(min(values), 1),
                    'max': round(max(values), 1),
                    'count': len(values)
                }

        return stats

