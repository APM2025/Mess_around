"""
Type-Aware CSV Cleaner

Properly handles 5 different CSV structures in COVER data.
Each type has different header rows, column positions, and data patterns.
"""

import pandas as pd
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from backend_code.database_src.csv_type_identifier import (
    identify_csv_type, get_structure_config, CSVStructureType
)


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


def load_cleaned_csv(csv_path: Path) -> Tuple[pd.DataFrame, List[Dict], CSVStructureType]:
    """
    Load and clean CSV using type-specific logic.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        (cleaned_df, vaccine_columns, csv_type)
        
    vaccine_columns structure:
        [
            {'col_idx': 6, 'header': 'Coverage at...', 'vaccine_name': 'DTaP/IPV/Hib/HepB'},
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
        # Columns 2+ are region names
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
        # Must be area code: E92000001, E10000019, etc.
        return bool(re.match(r'^[ESWN]\d{8}', value_str))
    
    elif csv_type == CSVStructureType.NATIONAL:
        # Country names
        countries = ['United Kingdom', 'England', 'Scotland', 'Wales', 'Northern Ireland']
        return value_str in countries
    
    elif csv_type in [CSVStructureType.TIME_SERIES, CSVStructureType.REGIONAL_TIME_SERIES]:
        # Financial year: "2009 to 2010" or "2009-2010"
        return bool(' to ' in value_str or re.match(r'^\d{4}-\d{4}$', value_str))
    
    elif csv_type == CSVStructureType.SPECIAL_PROGRAM:
        # Area codes
        return bool(re.match(r'^[ESWN]\d{8}', value_str))
    
    return False


def clean_numeric_value(value, decimal_places: int = None, return_range: bool = False):
    """
    Clean numeric value from CSV
    
    Handles:
    - Commas: '668,160' → 668160
    - Markers: [z], [c] → None
    - Ranges: "35% to 69%" → (None, "35% to 69%")
    - Long decimals: 94.03672966891358 → 94.04
    
    Examples:
        >>> clean_numeric_value("668,160")
        668160
        >>> clean_numeric_value("[c]")  # Suppressed data
        None
        >>> clean_numeric_value("94.037", decimal_places=2)
        94.04
        >>> clean_numeric_value("35% to 69%", return_range=True)
        (None, "35% to 69%")
    
    Args:
        value: Raw value from CSV
        decimal_places: Round to this many decimal places
        return_range: If True, return (value, range_text) tuple
    
    Returns:
        Cleaned value or None
    """
    if pd.isna(value):
        return (None, None) if return_range else None
    
    value_str = str(value).strip()
    
    # Check for markers
    if value_str in ['[z]', '[c]', '[x]', '', 'nan']:
        return (None, None) if return_range else None
    
    # Check for ranges
    if ' to ' in value_str:
        return (None, value_str) if return_range else None
    
    # Remove commas and percentage signs
    cleaned = value_str.replace(',', '').replace('%', '')
    
    try:
        result = float(cleaned)
        
        # Round if requested
        if decimal_places is not None:
            result = round(result, decimal_places)
        
        return (result, None) if return_range else result
    
    except ValueError:
        return (None, None) if return_range else None
