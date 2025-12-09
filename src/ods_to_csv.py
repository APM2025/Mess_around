"""
Data Access Layer - ODS to CSV Conversion

Handles conversion of COVER ODS file sheets to CSV format.
Each data sheet is converted separately for easier processing.

Sheet Mapping:
- T1_UK12m, T2_UK24m, T3_UK5y → national_coverage
- T4a_UTLA12m, T4b_UTLA12m, T5a_UTLA24m, T5b_UTLA24m, T6a_UTLA5y, T6b_UTLA5y → local_authority_coverage
- T9_Eng12m, T10_Eng24m, T11_Eng5y → england_time_series
- T14_RegDTaP24m, T15_RegMMR24m → regional_time_series
- T7_UTLAHepB, T8_UTLABCG → special_programs

Requirements:
- DA-FR-001: Load data from external files (ODS)
- DA-FR-002: Support multiple file formats (ODS → CSV)
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict


# Sheet categorization based on data analysis
DATA_SHEETS = {
    'national': ['T1_UK12m', 'T2_UK24m', 'T3_UK5y'],
    'local_authority': ['T4a_UTLA12m', 'T4b_UTLA12m', 'T5a_UTLA24m', 
                        'T5b_UTLA24m', 'T6a_UTLA5y', 'T6b_UTLA5y'],
    'england_time_series': ['T9_Eng12m', 'T10_Eng24m', 'T11_Eng5y'],
    'regional_time_series': ['T14_RegDTaP24m', 'T15_RegMMR24m'],
    'special_programs': ['T7_UTLAHepB', 'T8_UTLABCG']
}

# Metadata sheets (skip these)
METADATA_SHEETS = ['Cover', 'Contents', 'Notes', 'Revision_History']


def convert_ods_to_csv(ods_filepath, sheet_name=None, output_dir=None):
    """
    Convert ODS file sheet(s) to CSV format
    
    Args:
        ods_filepath: Path to ODS file
        sheet_name: Specific sheet to convert (None = convert all data sheets)
        output_dir: Directory for CSV output (default: same as ODS file)
    
    Returns:
        List of paths to created CSV files
    
    Requirement: DA-FR-002 (Support multiple file formats)
    """
    ods_filepath = Path(ods_filepath)
    
    if not ods_filepath.exists():
        raise FileNotFoundError(
            f"The ODS file was not found at: {ods_filepath}. "
            f"Please check the file path and try again."
        )
    
    if not str(ods_filepath).endswith('.ods'):
        raise ValueError(
            f"Expected an ODS file, but got: {ods_filepath.suffix}. "
            f"Please provide a file with .ods extension."
        )
    
    # Set output directory
    if output_dir is None:
        output_dir = ods_filepath.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load ODS file
    try:
        xls = pd.ExcelFile(ods_filepath, engine='odf')
    except ImportError as e:
        raise ImportError(
            "The 'odfpy' library is required to read ODS files. "
            "Please install it using: pip install odfpy"
        ) from e
    
    created_csvs = []
    
    # Determine which sheets to convert
    if sheet_name:
        sheets_to_convert = [sheet_name] if sheet_name in xls.sheet_names else []
        if not sheets_to_convert:
            raise ValueError(f"Sheet '{sheet_name}' not found in ODS file")
    else:
        # Convert all data sheets (skip metadata)
        all_data_sheets = []
        for category_sheets in DATA_SHEETS.values():
            all_data_sheets.extend(category_sheets)
        
        sheets_to_convert = [s for s in all_data_sheets if s in xls.sheet_names]
    
    # Convert each sheet
    for sheet in sheets_to_convert:
        # Read sheet
        df = pd.read_excel(ods_filepath, sheet_name=sheet, engine='odf')
        
        # Create CSV filename
        csv_filename = f"{ods_filepath.stem}_{sheet}.csv"
        csv_filepath = output_dir / csv_filename
        
        # Save to CSV
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        
        created_csvs.append(csv_filepath)
        print(f"✓ Converted: {sheet} → {csv_filename}")
    
    return created_csvs


def convert_all_data_sheets(ods_filepath, output_dir=None):
    """
    Convert all data sheets from ODS to CSV
    
    Args:
        ods_filepath: Path to ODS file
        output_dir: Directory for CSV output
    
    Returns:
        Dictionary mapping sheet categories to CSV file paths
    
    This is the main function to use for batch conversion.
    """
    ods_filepath = Path(ods_filepath)
    
    if output_dir is None:
        output_dir = ods_filepath.parent / "csv_data"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    converted_files = {
        'national': [],
        'local_authority': [],
        'england_time_series': [],
        'regional_time_series': [],
        'special_programs': []
    }
    
    print(f"\n{'='*80}")
    print("Converting COVER ODS Sheets to CSV")
    print(f"{'='*80}\n")
    
    for category, sheets in DATA_SHEETS.items():
        print(f"\n📊 {category.upper().replace('_', ' ')}:")
        
        for sheet in sheets:
            try:
                csv_path = convert_ods_to_csv(ods_filepath, sheet, output_dir)
                converted_files[category].extend(csv_path)
            except Exception as e:
                print(f"  ✗ Failed to convert {sheet}: {e}")
    
    print(f"\n{'='*80}")
    print(f"Conversion Complete! CSVs saved to: {output_dir}")
    print(f"{'='*80}\n")
    
    return converted_files


def load_csv_file(csv_filepath):
    """
    Load CSV file into pandas DataFrame
    
    Args:
        csv_filepath: Path to CSV file
    
    Returns:
        pandas DataFrame
    
    Requirement: DA-FR-001 (Load from external file)
    """
    csv_filepath = Path(csv_filepath)
    
    if not csv_filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_filepath}")
    
    df = pd.read_csv(csv_filepath)
    return df
