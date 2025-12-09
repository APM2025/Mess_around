"""
CSV Cleaning Functions

Cleans raw CSV data from COVER ODS sheets.

Functions for:
- Finding header rows
- Extracting vaccine names
- Cleaning numeric values
- Parsing note references
- Identifying data rows

Based on ODS File Mapping specification.

Requirements:
- DC-FR-001: Handle missing data
- DC-FR-002: Convert to correct types
"""

import pandas as pd
import re
from pathlib import Path
from typing import Optional, Tuple, List


def find_header_row(csv_path: Path, indicator: str = "Geographic") -> Optional[int]:
    """
    Find the header row in a CSV file
    
    Args:
        csv_path: Path to CSV file
        indicator: String that appears in header row
    
    Returns:
        Row index (0-based) of header, or None if not found
    
    Example:
        T1_UK12m has headers at row 4 containing "Geographic area"
        T4a_UTLA12m has headers at row 7 containing "Code"
        T9_Eng12m has headers at row 14 containing "Financial year"
    """
    df = pd.read_csv(csv_path, header=None)
    
    # Try multiple indicators for different sheet types
    indicators = [indicator, "Code", "Local authority", "Geographic area", "Financial year"]
    
    for idx, row in df.iterrows():
        # Check if any cell in this row contains any indicator
        for cell in row:
            if isinstance(cell, str):
                for ind in indicators:
                    if ind in cell:
                        return idx
    
    return None


def extract_vaccine_name(header: str) -> str:
    """
    Extract vaccine name from column header
    
    Args:
        header: Column header text
    
    Returns:
        Clean vaccine name
    
    """
    # Remove common prefixes (both "Coverage at" and "Coverage of" patterns)
    prefixes = [
        'Coverage at 12 months ',
        'Coverage at 24 months ',
        'Coverage at 5 years ',
        'Coverage of ',  # Time series pattern
        'Number aged 12 months ',
        'Number aged 24 months ',
        'Number aged 5 years '
    ]
    
    result = header
    for prefix in prefixes:
        result = result.replace(prefix, '')
    
    # Remove suffixes (but keep 'booster')
    result = result.replace(' Prim', '')
    result = result.replace(' (%)', '')
    result = result.replace('(%)', '')
    
    # Handle "rotavirus" vs "rota" (time series uses full name)
    if 'rotavirus' in result.lower():
        result = 'Rotavirus'
    
    return result.strip()


def clean_numeric_value(value, decimal_places: int = None, return_range: bool = False):
    """
    Clean numeric value from CSV
    
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
    if value_str in ['[z]', '[c]', '']:
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


def parse_note_reference(value) -> Optional[int]:
    """
    Parse note reference from cell value
    
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


def is_data_row(row: List) -> bool:
    """
    Check if row contains data (vs metadata/header)
    
    Args:
        row: List of cell values
    
    Returns:
        True if data row, False otherwise
    
    Rules:
        - Empty rows: False
        - Rows starting with area code (E followed by digits): True
        - Rows starting with financial year (YYYY to YYYY): True
        - Header rows (contain "Geographic", "Coverage", etc.): False
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
    if re.match(r'^[ESWN]\d{8}', first_cell):  # E92000001, E10000019, etc.
        return True
    
    # Financial year format: "2009 to 2010" or "2024-2025"
    if ' to ' in first_cell and any(char.isdigit() for char in first_cell):
        return True
    if re.match(r'^\d{4}-\d{4}$', first_cell):  # 2024-2025
        return True
    
    # Country names
    countries = ['United Kingdom', 'England', 'Scotland', 'Wales', 'Northern Ireland']
    if first_cell in countries:
        return True
    
    # If we get here, assume it's not a data row
    return False


def load_cleaned_csv(csv_path: Path, sheet_type: str = 'national') -> pd.DataFrame:
    """
    Load and clean an entire CSV file
    
    Args:
        csv_path: Path to CSV file
        sheet_type: Type of sheet ('national', 'utla', 'time_series', 'special')
    
    Returns:
        Cleaned DataFrame with:
        - Proper column names
        - Only data rows
        - Cleaned numeric values
    
    """
    # Find where headers are
    header_row_idx = find_header_row(csv_path)
    
    if header_row_idx is None:
        # Fallback: assume headers at row 0
        header_row_idx = 0
    
    # Load CSV with correct header
    df = pd.read_csv(csv_path, header=header_row_idx)
    
    # Rename first column to 'area_name' or 'area_code' depending on content
    if len(df.columns) > 0:
        first_col = df.columns[0]
        # Check if first column looks like codes or names
        first_values = df[first_col].dropna()
        if len(first_values) > 0:
            sample = str(first_values.iloc[0]).strip()
            
            # Match ANY UK area code format: E/S/W/N followed by 8 digits
            # This includes countries (E92, S92), regions (E12), and UTLAs (E06/08/09/10)
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
