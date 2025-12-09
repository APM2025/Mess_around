"""
CSV Type Identification

Determines which COVER sheet structure a CSV file uses and provides
type-specific configurations.
"""

from pathlib import Path
from enum import Enum
from typing import Dict, Optional


class CSVStructureType(Enum):
    """Types of CSV structures in COVER data"""
    NATIONAL = "national"  # T1, T2, T3
    LOCAL_AUTHORITY = "local_authority"  # T4a, T4b, T5a, T5b, T6a, T6b
    TIME_SERIES = "time_series"  # T9, T10, T11
    REGIONAL_TIME_SERIES = "regional_time_series"  # T14, T15
    SPECIAL_PROGRAM = "special_program"  # T7, T8
    UNKNOWN = "unknown"


def identify_csv_type(csv_path: Path) -> CSVStructureType:
    """
    Identify CSV structure type from filename.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        CSVStructureType enum
    
    Examples:
        T1_UK12m.csv → NATIONAL
        T4a_UTLA12m.csv → LOCAL_AUTHORITY
        T9_Eng12m.csv → TIME_SERIES
        T14_RegDTaP24m.csv → REGIONAL_TIME_SERIES
    """
    filename = csv_path.name
    
    # National coverage (UK countries)
    if any(filename.startswith(prefix) for prefix in ['T1_', 'T2_', 'T3_']):
        return CSVStructureType.NATIONAL
    
    # Local authority coverage
    if any(filename.startswith(prefix) for prefix in ['T4', 'T5', 'T6']):
        return CSVStructureType.LOCAL_AUTHORITY
    
    # Special programs (HepB, BCG)
    if any(filename.startswith(prefix) for prefix in ['T7_', 'T8_']):
        return CSVStructureType.SPECIAL_PROGRAM
    
    # England time series
    if any(filename.startswith(prefix) for prefix in ['T9_', 'T10_', 'T11_']):
        return CSVStructureType.TIME_SERIES
    
    # Regional time series (check for T14 or T15 anywhere in filename)
    if 'T14_' in filename or 'T15_' in filename:
        return CSVStructureType.REGIONAL_TIME_SERIES
    
    return CSVStructureType.UNKNOWN


def get_structure_config(csv_type: CSVStructureType) -> Dict:
    """
    Get configuration for each CSV structure type.
    
    Returns dict with:
        - header_indicator: What to look for in header row
        - vaccine_col_start: Which column vaccines start at (CRITICAL!)
        - identifier_col: What the first column contains
        - header_pattern: How vaccine names appear in headers
    """
    configs = {
        CSVStructureType.NATIONAL: {
            'header_indicator': 'Geographic area',
            'vaccine_col_start': 3,  # Vaccines at column 3
            'identifier_col': 'area_name',
            'population_col': 2,
            'header_pattern': 'Coverage at',  # "Coverage at 12 months X"
        },
        
        CSVStructureType.LOCAL_AUTHORITY: {
            'header_indicator': 'Code',
            'vaccine_col_start': 6,  # Vaccines at column 6! NOT 3!
            'identifier_col': 'area_code',
            'area_name_col': 1,
            'region_col': 2,
            'ods_col': 3,
            'population_col': 5,
            'header_pattern': 'Coverage at',
        },
        
        CSVStructureType.TIME_SERIES: {
            'header_indicator': 'Financial year',
            'vaccine_col_start': 3,  # Vaccines at column 3
            'identifier_col': 'year',
            'population_col': 2,
            'header_pattern': 'Coverage of',  # Different pattern!
        },
        
        CSVStructureType.REGIONAL_TIME_SERIES: {
            'header_indicator': 'Financial year',  # Row 17
            'vaccine_col_start': 2,  # Regions start at column 2 (NOT vaccines!)
            'identifier_col': 'year',
            'notes_col': 1,
            'header_pattern': None,  # Regions, not vaccines!
            'transpose_structure': True,  # Years in rows, regions in columns
        },
        
        CSVStructureType.SPECIAL_PROGRAM: {
            'header_indicator': 'Code',
            'vaccine_col_start': 5,
            'identifier_col': 'area_code',
            'header_pattern': 'Coverage at',
        }
    }
    
    return configs.get(csv_type, {})
