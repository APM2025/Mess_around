"""
Update Imports Script

Updates all import statements in database_version_2 to use the new structure.

Old: from backend_code.database_src.X import Y
New: from database_version_2.src.X import Y
"""

import re
from pathlib import Path

def update_imports_in_file(file_path: Path):
    """Update imports in a single file."""
    print(f"Processing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: from backend_code.database_src.X import Y
    content = re.sub(
        r'from backend_code\.database_src\.(\w+) import',
        r'from database_version_2.src.\1 import',
        content
    )
    
    # Pattern 2: import backend_code.database_src.X
    content = re.sub(
        r'import backend_code\.database_src\.(\w+)',
        r'import database_version_2.src.\1',
        content
    )
    
    # Special case: csv_data_loader -> csv_loader_base
    content = content.replace(
        'from database_version_2.src.csv_data_loader import',
        'from database_version_2.src.csv_loader_base import'
    )
    
    # Special case: vaccine_reference -> vaccine_matcher
    content = content.replace(
        'from database_version_2.src.vaccine_reference import',
        'from database_version_2.src.vaccine_matcher import'
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated")
        return True
    else:
        print(f"  - No changes needed")
        return False

def main():
    """Update all files in database_version_2."""
    base_dir = Path(__file__).parent / "database_version_2"
    
    # Update source files
    src_dir = base_dir / "src"
    test_dir = base_dir / "tests"
    
    updated_count = 0
    
    print("\n=== Updating Source Files ===")
    for file_path in src_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            if update_imports_in_file(file_path):
                updated_count += 1
    
    print("\n=== Updating Test Files ===")
    for file_path in test_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            if update_imports_in_file(file_path):
                updated_count += 1
    
    print(f"\n✓ Updated {updated_count} files")

if __name__ == "__main__":
    main()
