"""
CSV Cleaning Functions - Unified Type-Aware Version

Handles all 5 different CSV structures in COVER data:
1. National coverage (UK/countries)
2. Local authority coverage (UTLAs)
3. England time series (historical)
4. Regional time series (historical by region)
5. Special programs (HepB, BCG)

Each type has different header rows, column positions, and data patterns.
This module automatically detects the type and applies appropriate cleaning.
"""

import pandas as pd
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from enum import Enum


# =============================================================================
# CSV Type Identification
# =============================================================================

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
    
    # Regional time series
    if 'T14_' in filename or 'T15_' in filename:
        return CSVStructureType.REGIONAL_TIME_SERIES
    
    return CSVStructureType.UNKNOWN


def get_structure_config(csv_type: CSVStructureType) -> Dict:
    """
    Get configuration for each CSV structure type.
    
    Returns dict with:
        - header_indicator: What to look for in header row
        - vaccine_col_start: Which column vaccines/regions start at
        - identifier_col: What the first column contains
        - header_pattern: How vaccine names appear in headers
    """
    configs = {
        CSVStructureType.NATIONAL: {
            'header_indicator': 'Geographic area',
            'vaccine_col_start': 3,
            'identifier_col': 'area_name',
            'population_col': 2,
            'header_pattern': 'Coverage at',
        },
        
        CSVStructureType.LOCAL_AUTHORITY: {
            'header_indicator': 'Code',
            'vaccine_col_start': 6,  # CRITICAL: Column 6, not 3!
            'identifier_col': 'area_code',
            'area_name_col': 1,
            'region_col': 2,
            'ods_col': 3,
            'population_col': 5,
            'header_pattern': 'Coverage at',
        },
        
        CSVStructureType.TIME_SERIES: {
            'header_indicator': 'Financial year',
            'vaccine_col_start': 3,
            'identifier_col': 'year',
            'population_col': 2,
            'header_pattern': 'Coverage of',  # Different pattern!
        },
        
        CSVStructureType.REGIONAL_TIME_SERIES: {
            'header_indicator': 'Financial year',
            'vaccine_col_start': 2,  # Regions start at column 2
            'identifier_col': 'year',
            'notes_col': 1,
            'header_pattern': None,  # Regions, not vaccines!
            'transpose_structure': True,
        },
        
        CSVStructureType.SPECIAL_PROGRAM: {
            'header_indicator': 'Code',
            'vaccine_col_start': 5,
            'identifier_col': 'area_code',
            'header_pattern': 'Coverage at',
        }
    }
    
    return configs.get(csv_type, {})


# =============================================================================
# Type-Aware CSV Cleaning Functions
# =============================================================================

def find_header_row(csv_path: Path, indicator: str = "Geographic") -> Optional[int]:
    """
    Find the header row in a CSV file (simple version for backward compatibility).
    
    Args:
        csv_path: Path to CSV file
        indicator: String that appears in header row
    
    Returns:
        Row index (0-based) of header, or None if not found
    """
    df = pd.read_csv(csv_path, header=None)
    
    # Try multiple indicators for different sheet types
    indicators = [indicator, "Code", "Local authority", "Geographic area", "Financial year"]
    
    for idx, row in df.iterrows():
        for cell in row:
            if isinstance(cell, str):
                for ind in indicators:
                    if ind in cell:
                        return idx
    
    return None


def find_header_row_typed(csv_path: Path, csv_type: CSVStructureType) -> Optional[int]:
    """
    Find header row based on CSV type.
    
    Args:
        csv_path: Path to CSV
        csv_type: CSV structure type
    
    Returns:
        Row index of header
    """
    df = pd.read_csv(csv_path, header=None)
    config = get_structure_config(csv_type)
    indicator = config.get('header_indicator', 'Geographic')
    
    for idx, row in df.iterrows():
        for cell in row:
            if isinstance(cell, str) and indicator in cell:
                return idx
    
    return None


def extract_vaccine_name(header: str) -> str:
    """
    Extract vaccine name from column header (simple version).
    
    Args:
        header: Column header text
    
    Returns:
        Clean vaccine name
    """
    # Remove common prefixes
    prefixes = [
        'Coverage at 12 months ',
        'Coverage at 24 months ',
        'Coverage at 5 years ',
        'Coverage of ',
        'Number aged 12 months ',
        'Number aged 24 months ',
        'Number aged 5 years '
    ]
    
    result = header
    for prefix in prefixes:
        result = result.replace(prefix, '')
    
    # Remove suffixes
    result = result.replace(' Prim', '')
    result = result.replace(' (%)', '')
    result = result.replace('(%)', '')
    
    # Handle rotavirus
    if 'rotavirus' in result.lower():
        result = 'Rotavirus'
    
    return result.strip()


def extract_vaccine_name_typed(header: str, csv_type: CSVStructureType) -> str:
    """
    Extract vaccine name using type-specific pattern.
    
    Args:
        header: Column header text
        csv_type: CSV structure type
    
    Returns:
        Clean vaccine name
    """
    config = get_structure_config(csv_type)
    header_pattern = config.get('header_pattern', 'Coverage at')
    
    result = header
    
    # Different patterns for different types
    if header_pattern == 'Coverage of':
        # Time series: "Coverage of DTaP/IPV/Hib/HepB (%)"
        result = result.replace('Coverage of ', '')
    elif header_pattern == 'Coverage at':
        # National/Local: "Coverage at 12 months DTaP/IPV/Hib/HepB (%)"
        prefixes = [
            'Coverage at 12 months ',
            'Coverage at 24 months ',
            'Coverage at 5 years ',
            'Number aged 12 months ',
            'Number aged 24 months ',
        ]
        for prefix in prefixes:
            result = result.replace(prefix, '')
    
    # Remove common suffixes
    result = result.replace(' Prim', '')
    result = result.replace(' (%)', '')
    result = result.replace('(%)', '')
    result = result.strip()
    
    # Handle rotavirus naming
    if 'rotavirus' in result.lower():
        result = 'Rotavirus'
    
    return result


def clean_numeric_value(value, decimal_places: int = None, return_range: bool = False):
    """
    Clean numeric value from CSV.
    
    Handles:
    - Commas: '668,160' → 668160
    - Markers: [z], [c] → None
    - Ranges: "35% to 69%" → (None, "35% to 69%")
    - Long decimals: 94.03672966891358 → 94.04
    
    Args:
        value: Raw value from CSV
        decimal_places: Round to this many decimal places
        return_range: If True, return (value, range_text) tuple
    
    Returns:
        Cleaned value or None
    """
    # Handle None/NaN
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return (None, None) if return_range else None
    
    # Convert to string for processing
    value_str = str(value).strip()
    
    # Handle markers
    if value_str in ['[z]', '[c]', '[x]', '', 'nan']:
        return (None, None) if return_range else None
    
    # Handle percentage ranges
    if 'to' in value_str and '%' in value_str:
        if return_range:
            return (None, value_str)
        else:
            return None
    
    # Remove commas
    value_str = value_str.replace(',', '')
    
    # Try to convert to number
    try:
        # Try float first
        if '.' in value_str:
            num = float(value_str)
            if decimal_places is not None:
                num = round(num, decimal_places)
        else:
            num = int(value_str)
        
        return (num, None) if return_range else num
    
    except ValueError:
        # Not a number
        return (None, None) if return_range else None


def is_data_row(row: List) -> bool:
    """
    Check if row contains data (vs metadata/header) - simple version.
    
    Args:
        row: List of cell values
    
    Returns:
        True if data row, False otherwise
    """
    # Empty row check
    if not row or len(row) == 0:
        return False
    
    # All None/empty check
    if all(cell is None or (isinstance(cell, str) and cell.strip() == '') for cell in row):
        return False
    
    # Get first non-empty cell
    first_cell = None
    for cell in row:
        if cell is not None and (not isinstance(cell, str) or cell.strip() != ''):
            first_cell = str(cell).strip()
            break
    
    if not first_cell:
        return False
    
    # Header indicators
    header_keywords = ['Geographic', 'Coverage', 'Financial year', 'Local authority', 
                      'Number aged', 'Evaluation', 'Code', 'Unnamed']
    if any(keyword in first_cell for keyword in header_keywords):
        return False
    
    # Data row indicators
    # UK area codes start with E, S, W, N followed by numbers
    if re.match(r'^[ESWN]\d{8}', first_cell):
        return True
    
    # Financial year format
    if ' to ' in first_cell and any(char.isdigit() for char in first_cell):
        return True
    if re.match(r'^\d{4}-\d{4}$', first_cell):
        return True
    
    # Country names
    countries = ['United Kingdom', 'England', 'Scotland', 'Wales', 'Northern Ireland']
    if first_cell in countries:
        return True
    
    return False


def is_data_row_typed(row: pd.Series, csv_type: CSVStructureType, first_col_name: str) -> bool:
    """
    Check if row is data using type-specific logic.
    
    Args:
        row: DataFrame row
        csv_type: CSV structure type
        first_col_name: Name of first column
    
    Returns:
        True if data row
    """
    # Get first column value
    if first_col_name not in row.index:
        return False
    
    value = row[first_col_name]
    
    # Empty check
    if pd.isna(value) or str(value).strip() == '':
        return False
    
    value_str = str(value).strip()
    
    # Header keywords (always skip)
    header_keywords = ['Geographic', 'Coverage', 'Financial year', 'Local authority',
                      'Number aged', 'Evaluation', 'Code', 'Unnamed']
    if any(keyword in value_str for keyword in header_keywords):
        return False
    
    # Type-specific checks
    if csv_type == CSVStructureType.LOCAL_AUTHORITY:
        # Must be area code
        return bool(re.match(r'^[ESWN]\d{8}', value_str))
    
    elif csv_type == CSVStructureType.NATIONAL:
        # Country names
        countries = ['United Kingdom', 'England', 'Scotland', 'Wales', 'Northern Ireland']
        return value_str in countries
    
    elif csv_type in [CSVStructureType.TIME_SERIES, CSVStructureType.REGIONAL_TIME_SERIES]:
        # Financial year
        return bool(' to ' in value_str or re.match(r'^\d{4}-\d{4}$', value_str))
    
    elif csv_type == CSVStructureType.SPECIAL_PROGRAM:
        # Area codes
        return bool(re.match(r'^[ESWN]\d{8}', value_str))
    
    return False


def load_cleaned_csv(csv_path: Path, sheet_type: str = 'national') -> pd.DataFrame:
    """
    Load and clean CSV file (simple version for backward compatibility).
    
    Args:
        csv_path: Path to CSV file
        sheet_type: Type of sheet (ignored, auto-detected)
    
    Returns:
        Cleaned DataFrame
    """
    # Find where headers are
    header_row_idx = find_header_row(csv_path)
    
    if header_row_idx is None:
        header_row_idx = 0
    
    # Load CSV with correct header
    df = pd.read_csv(csv_path, header=header_row_idx)
    
    # Rename first column
    if len(df.columns) > 0:
        first_col = df.columns[0]
        first_values = df[first_col].dropna()
        if len(first_values) > 0:
            sample = str(first_values.iloc[0]).strip()
            
            if re.match(r'^[ESWN]\d{8}', sample):
                df.rename(columns={first_col: 'area_code'}, inplace=True)
            else:
                df.rename(columns={first_col: 'area_name'}, inplace=True)
    
    # Filter to data rows only
    data_rows = []
    for idx, row in df.iterrows():
        if is_data_row(row.tolist()):
            data_rows.append(row)
    
    if data_rows:
        df_clean = pd.DataFrame(data_rows)
    else:
        df_clean = pd.DataFrame()
    
    return df_clean


def load_cleaned_csv_typed(csv_path: Path) -> Tuple[pd.DataFrame, List[Dict], CSVStructureType]:
    """
    Load and clean CSV using type-specific logic (advanced version).
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        (cleaned_df, vaccine_columns, csv_type)
        
    vaccine_columns structure:
        [
            {'col_idx': 6, 'header': 'Coverage at...', 'vaccine_name': 'DTaP/IPV/Hib/HepB'},
            ...
        ]
        
    For regional time series:
        [
            {'col_idx': 2, 'header': 'East Midlands', 'region_name': 'East Midlands'},
            ...
        ]
    """
    # Identify type
    csv_type = identify_csv_type(csv_path)
    config = get_structure_config(csv_type)
    
    print(f"\n[CSV Type: {csv_type.value}] {csv_path.name}")
    
    # Find header row
    header_row_idx = find_header_row_typed(csv_path, csv_type)
    if header_row_idx is None:
        print(f"  WARNING: Header not found, using row 0")
        header_row_idx = 0
    else:
        print(f"  Header row: {header_row_idx}")
    
    # Load with correct header
    df = pd.read_csv(csv_path, header=header_row_idx)
    
    vaccine_columns = []
    
    # Extract vaccine columns (type-specific!)
    if csv_type == CSVStructureType.REGIONAL_TIME_SERIES:
        # Special case: regions as columns, not vaccines!
        vaccine_col_start = config.get('vaccine_col_start', 2)
        print(f"  Regional TS: columns {vaccine_col_start}+ are REGIONS")
        
        for col_idx in range(vaccine_col_start, len(df.columns)):
            region_name = str(df.columns[col_idx]).strip()
            
            # Skip notes column
            if 'note' in region_name.lower() or region_name == '':
                continue
            
            vaccine_columns.append({
                'col_idx': col_idx,
                'header': region_name,
                'region_name': region_name  # Not vaccine_name!
            })
        
        print(f"  Found {len(vaccine_columns)} region columns")
    
    else:
        # Normal case: vaccines as columns
        vaccine_col_start = config.get('vaccine_col_start', 3)
        print(f"  Vaccine columns start at: {vaccine_col_start}")
        
        for col_idx in range(vaccine_col_start, len(df.columns)):
            header = str(df.columns[col_idx])
            
            # Skip non-vaccine columns
            if any(skip in header for skip in ['Note', 'Unnamed', 'nan']):
                continue
            
            vaccine_name = extract_vaccine_name_typed(header, csv_type)
            
            if vaccine_name:
                vaccine_columns.append({
                    'col_idx': col_idx,
                    'header': header,
                    'vaccine_name': vaccine_name
                })
        
        print(f"  Found {len(vaccine_columns)} vaccine columns")
    
    # Filter to data rows only
    df_filtered = df[df.apply(lambda row: is_data_row_typed(row, csv_type, df.columns[0]), axis=1)].copy()
    
    print(f"  Rows: {len(df)} -> {len(df_filtered)} (filtered)")
    
    return df_filtered, vaccine_columns, csv_type


def parse_note_reference(value) -> Optional[int]:
    """
    Parse note reference from cell value.
    
    Args:
        value: Cell value
    
    Returns:
        Note number if found, else None
    """
    if not isinstance(value, str):
        return None
    
    match = re.search(r'\[note (\d+)\]', value)
    if match:
        return int(match.group(1))
    
    return None
