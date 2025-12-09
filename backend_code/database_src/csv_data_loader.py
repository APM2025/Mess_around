"""
Abstract base class for CSV data loaders.

Implements Template Method pattern to eliminate code duplication across
multiple loader modules.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session

from backend_code.database_src.csv_cleaner import load_cleaned_csv
from backend_code.database_src.models import AgeCohort, FinancialYear


class CSVDataLoader(ABC):
    """
    Abstract base class for loading CSV data into database.
    
    Template Method pattern: defines skeleton of loading algorithm,
    with subclasses providing specific implementations.
    """
    
    def __init__(self, session: Session, csv_path: Path):
        """
        Initialize loader.
        
        Args:
            session: SQLAlchemy database session
            csv_path: Path to CSV file to load
        """
        self.session = session
        self.csv_path = csv_path
        self.df = None
        
    def load(self) -> None:
        """
        Main loading workflow (Template Method).
        
        Defines the algorithm structure while allowing subclasses
        to customize specific steps.
        """
        # 1. Load and validate CSV
        self.df = self._load_csv()
        if not self._validate_dataframe():
            return
        
        # 2. Get reference data
        self._load_reference_data()
        
        # 3. Process rows (subclass-specific)
        for idx, row in self.df.iterrows():
            try:
                self._process_row(idx, row)
            except Exception as e:
                self._handle_row_error(idx, row, e)
        
        # 4. Commit changes
        self.session.commit()
    
    def _load_csv(self) -> pd.DataFrame:
        """Load CSV with appropriate sheet type."""
        sheet_type = self._get_sheet_type()
        return load_cleaned_csv(self.csv_path, sheet_type=sheet_type)
    
    def _validate_dataframe(self) -> bool:
        """Check if dataframe has data."""
        return self.df is not None and not self.df.empty
    
    @abstractmethod
    def _get_sheet_type(self) -> str:
        """
        Return CSV sheet type.
        
        Returns:
            One of: 'national', 'local_authority', 'time_series', 
                   'regional_time_series', 'special_program'
        """
        pass
    
    @abstractmethod
    def _load_reference_data(self) -> None:
        """
        Load and cache reference data (cohorts, years, etc).
        
        This is called once before processing rows.
        """
        pass
    
    @abstractmethod
    def _process_row(self, idx: int, row: pd.Series) -> None:
        """
        Process a single data row.
        
        Args:
            idx: Row index in dataframe
            row: Row data as pandas Series
        """
        pass
    
    def _handle_row_error(self, idx: int, row: pd.Series, error: Exception) -> None:
        """
        Handle row processing errors (default: log and continue).
        
        Args:
            idx: Row index
            row: Row data
            error: Exception that occurred
        """
        print(f"Warning: Error processing row {idx}: {error}")
    
    def _determine_cohort_from_filename(self) -> int:
        """
        Extract cohort age (in months) from filename.
        
        Returns:
            Age in months (12, 24, 60, or 3)
        
        Raises:
            ValueError: If cohort cannot be determined
        """
        filename = self.csv_path.stem.lower()
        if '12m' in filename:
            return 12
        elif '24m' in filename:
            return 24
        elif '5y' in filename:
            return 60
        elif '3m' in filename:
            return 3
        else:
            raise ValueError(f"Cannot determine cohort from {filename}")
    
    def _get_cohort(self, age_months: int) -> Optional[AgeCohort]:
        """
        Get cohort from database by age in months.
        
        Args:
            age_months: Age in months
        
        Returns:
            AgeCohort instance or None
        """
        return self.session.query(AgeCohort)\
            .filter_by(age_months=age_months).first()
    
    def _get_financial_year(self, year_label: str) -> Optional[FinancialYear]:
        """
        Get financial year from database.
        
        Args:
            year_label: Year label like "2024-2025"
        
        Returns:
            FinancialYear instance or None
        """
        return self.session.query(FinancialYear)\
            .filter_by(year_label=year_label).first()
    
    @staticmethod
    def _normalize_year_label(year_str: str) -> str:
        """
        Normalize year label format.
        
        Converts "2009 to 2010" -> "2009-2010"
        
        Args:
            year_str: Year string in various formats
        
        Returns:
            Normalized year label
        """
        if ' to ' in year_str:
            parts = year_str.split(' to ')
            if len(parts) == 2:
                return f"{parts[0].strip()}-{parts[1].strip()}"
        return year_str
