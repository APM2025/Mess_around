"""
Data export module for exporting filtered vaccination data to CSV.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any


class DataExporter:
    """Exports vaccination data to various formats."""

    def __init__(self):
        """Initialize data exporter."""
        pass

    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        output_file: Path,
        encoding: str = 'utf-8'
    ) -> Path:
        """
        Export data to CSV file.

        Args:
            data: List of dictionaries to export
            output_file: Path to output CSV file
            encoding: File encoding (default: utf-8)

        Returns:
            Path to created CSV file
        """
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Handle empty data
        if not data:
            # Create empty file with no content
            output_file.write_text('', encoding=encoding)
            return output_file

        # Get fieldnames from first row
        fieldnames = list(data[0].keys())

        # Write CSV
        with open(output_file, 'w', newline='', encoding=encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return output_file
