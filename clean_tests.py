"""
Bulk cleanup script for removing emoji markers from test docstrings.
"""

import re
from pathlib import Path

def clean_docstring(content):
    """Remove TDD markers and emojis from Python docstrings."""
    
    # Remove TDD Phase lines with emojis
    content = re.sub(r'TDD Phase: RED 🔴.*?\n', '', content)
    content = re.sub(r'TDD Phase: GREEN ✓.*?\n', '', content)
    
    # Remove "RED 🔴:" prefixes from docstrings
    content = re.sub(r'RED 🔴: ', '', content)
    content = re.sub(r'GREEN ✓: ', '', content  )
    
    # Remove standalone emoji lines
    content = re.sub(r'\s*🔴\s*\n', '\n', content)
    content = re.sub(r'\s*✓\s*\n', '\n', content)
    
    return content

# Test files to process
test_dir = Path('tests/tests_database')
test_files = [
    'test_database.py',
    'test_models.py',
    'test_ods_conversion.py',
    'test_load_england_time_series.py',
    'test_load_regional_time_series.py',
    'test_load_local_authority.py',
    'test_load_national_coverage.py',
    'test_load_special_programs.py',
]

for filename in test_files:
    filepath = test_dir / filename
    if filepath.exists():
        print(f"Cleaning {filename}...")
        content = filepath.read_text(encoding='utf-8')
        cleaned = clean_docstring(content)
        filepath.write_text(cleaned, encoding='utf-8')
        print(f"  ✓ Done")

print("\nAll test files cleaned!")
