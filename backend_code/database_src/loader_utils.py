"""
Common utility functions for data loaders.

Provides shared helper functions to reduce code duplication across loader modules.
"""

from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from backend_code.database_src.models import AgeCohort, FinancialYear


def determine_cohort_from_filename(csv_path: Path) -> int:
    """
    Extract cohort age (in months) from CSV filename.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        Age in months (12, 24, 60, or 3)
    
    Raises:
        ValueError: If cohort cannot be determined from filename
    
    Examples:
        "T9_Eng12m.csv" -> 12
        "T10_Eng24m.csv" -> 24
        "T11_Eng5y.csv" -> 60
    """
    filename = csv_path.stem.lower()
    
    if '12m' in filename:
        return 12
    elif '24m' in filename:
        return 24
    elif '5y' in filename:
        return 60
    elif '3m' in filename:
        return 3
    else:
        raise ValueError(f"Cannot determine cohort from filename: {csv_path.name}")


def get_cohort(session: Session, age_months: int) -> Optional[AgeCohort]:
    """
    Get age cohort from database.
    
    Args:
        session: Database session
        age_months: Age in months
    
    Returns:
        AgeCohort instance or None if not found
    """
    return session.query(AgeCohort).filter_by(age_months=age_months).first()


def get_financial_year(session: Session, year_label: str) -> Optional[FinancialYear]:
    """
    Get financial year from database.
    
    Args:
        session: Database session
        year_label: Year label like "2024-2025"
    
    Returns:
        FinancialYear instance or None if not found
    """
    return session.query(FinancialYear).filter_by(year_label=year_label).first()


def normalize_year_label(year_str: str) -> str:
    """
    Normalize year label to standard format.
    
    Converts various year formats to "YYYY-YYYY" format.
    
    Args:
        year_str: Year string in various formats
    
    Returns:
        Normalized year label in "YYYY-YYYY" format
    
    Examples:
        "2009 to 2010" -> "2009-2010"
        "2024-2025" -> "2024-2025"
    """
    if ' to ' in year_str:
        parts = year_str.split(' to ')
        if len(parts) == 2:
            return f"{parts[0].strip()}-{parts[1].strip()}"
    return year_str


def validate_coverage_percentage(value: float) -> bool:
    """
    Validate that coverage percentage is in valid range.
    
    Args:
        value: Coverage percentage value
    
    Returns:
        True if valid (0-100 or None), False otherwise
    """
    if value is None:
        return True
    return 0 <= value <= 100
