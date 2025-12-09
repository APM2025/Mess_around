"""
England Time Series Data Loader - Refactored Version

Uses CSVDataLoader base class to eliminate code duplication.
"""

from pathlib import Path
from sqlalchemy.orm import Session
import pandas as pd

from backend_code.database_src.csv_data_loader import CSVDataLoader
from backend_code.database_src.models import EnglandTimeSeries, Vaccine
from backend_code.database_src.csv_cleaner import clean_numeric_value
from backend_code.database_src.vaccine_reference import match_vaccine_from_header


class EnglandTimeSeriesLoader(CSVDataLoader):
    """Loads England historical time series data (2009-2025)."""
    
    def __init__(self, session: Session, csv_path: Path):
        super().__init__(session, csv_path)
        self.cohort = None
        self.vaccine_columns = []
    
    def _get_sheet_type(self) -> str:
        return 'time_series'
    
    def _load_reference_data(self) -> None:
        """Load cohort and identify vaccine columns."""
        # Get cohort
        cohort_months = self._determine_cohort_from_filename()
        self.cohort = self._get_cohort(cohort_months)
        
        if not self.cohort:
            raise ValueError(f"Cohort {cohort_months} months not found")
        
        # Identify vaccine columns (skip first column which is year)
        for col in self.df.columns[1:]:
            vaccine_code = match_vaccine_from_header(col)
            if vaccine_code:
                self.vaccine_columns.append((col, vaccine_code))
    
    def _process_row(self, idx: int, row: pd.Series) -> None:
        """Process one year of England time series data."""
        # Get year label
        year_label = self._normalize_year_label(str(row.iloc[0]))
        
        # Skip non-year rows
        if not (' to ' in str(row.iloc[0]) or '-' in str(row.iloc[0])):
            return
        
        # Find financial year in database
        year = self._get_financial_year(year_label)
        if not year:
            return  # Skip years not in reference data
        
        # Process each vaccine
        for col_name, vaccine_code in self.vaccine_columns:
            self._process_vaccine_data(year, col_name, vaccine_code, row)
    
    def _process_vaccine_data(self, year, col_name, vaccine_code, row):
        """Process vaccine data for a specific year."""
        # Get vaccine from database
        vaccine = self.session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
        if not vaccine:
            return
        
        # Get coverage percentage
        coverage_value = row[col_name]
        coverage_pct = clean_numeric_value(coverage_value, decimal_places=2)
        
        # Validate percentage range
        if coverage_pct is not None and not (0 <= coverage_pct <= 100):
            return  # Skip invalid values
        
        # Check if record exists
        existing = self.session.query(EnglandTimeSeries).filter_by(
            year_id=year.year_id,
            cohort_id=self.cohort.cohort_id,
            vaccine_id=vaccine.vaccine_id
        ).first()
        
        if existing:
            # Update
            existing.coverage_percentage = coverage_pct
        else:
            # Create new
            record = EnglandTimeSeries(
                year_id=year.year_id,
                cohort_id=self.cohort.cohort_id,
                vaccine_id=vaccine.vaccine_id,
                coverage_percentage=coverage_pct
            )
            self.session.add(record)


def load_england_time_series_from_csv(csv_path: Path, session: Session) -> None:
    """
    Load England time series from a single CSV file.
    
    Args:
        csv_path: Path to T9/T10/T11 CSV file
        session: SQLAlchemy session
    """
    loader = EnglandTimeSeriesLoader(session, csv_path)
    loader.load()


def load_all_england_time_series(csv_dir: Path, session: Session) -> None:
    """
    Load all England time series sheets.
    
    Args:
        csv_dir: Directory containing CSV files
        session: SQLAlchemy session
    """
    csv_dir = Path(csv_dir)
    
    sheets = [
        'cover-anual-data-tables-2024-to-2025_T9_Eng12m.csv',
        'cover-anual-data-tables-2024-to-2025_T10_Eng24m.csv',
        'cover-anual-data-tables-2024-to-2025_T11_Eng5y.csv'
    ]
    
    for sheet_name in sheets:
        csv_path = csv_dir / sheet_name
        if csv_path.exists():
            print(f"Loading {sheet_name}...")
            load_england_time_series_from_csv(csv_path, session)
        else:
            print(f"Warning: {sheet_name} not found")
    
    print("England time series data loaded")
