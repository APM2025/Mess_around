"""
Bulk cleanup script for source code docstrings.
"""

import re
from pathlib import Path

def clean_source_docstrings(content):
    """Simplify verbose docstrings in source files."""
    
    # Remove overly verbose example sections with multiple examples
    # Pattern: >>> examples followed by output
    content = re.sub(
        r'    Examples:\s*\n(?:        .*\n)+',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # Simplify "Process:" sections in docstrings (step-by-step implementation details)
    content = re.sub(
        r'    Process:\s*\n(?:        \d+\..*\n)+',
        '',
        content,
        flags=re.MULTILINE
    )
    
    return content

# Source files to process
src_dir = Path('backend_code/database_src')
source_files = [
    'csv_cleaner.py',
    'load_reference_data.py',
    'load_england_time_series.py',
    'load_regional_time_series.py',
    'load_local_authority.py',
    'load_national_coverage.py',
    'load_special_programs.py',
    'ods_to_csv.py',
]

for filename in source_files:
    filepath = src_dir / filename
    if filepath.exists():
        print(f"Cleaning {filename}...")
        try:
            content = filepath.read_text(encoding='utf-8')
            cleaned = clean_source_docstrings(content)
            
            if content != cleaned:
                filepath.write_text(cleaned, encoding='utf-8')
                print(f"  ✓ Cleaned")
            else:
                print(f"  - No changes needed")
        except Exception as e:
            print(f"  ✗ Error: {e}")

print("\nSource file cleanup complete!")
