"""
Visualization module for vaccination coverage data.
"""

from pathlib import Path
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


class VaccinationVisualizer:
    """Creates visualizations for vaccination coverage data."""

    def __init__(self, output_dir: Path = None):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save charts (default: current directory)
        """
        self.output_dir = output_dir if output_dir else Path(".")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_top_areas(
        self,
        data: List[Dict[str, Any]],
        title: str = "Top Performing Areas",
        filename: str = "top_areas.png"
    ) -> Path:
        """
        Create horizontal bar chart for top performing areas.

        Args:
            data: List of dicts with 'area_name' and 'coverage' keys
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart file
        """
        # Extract data
        areas = [d['area_name'] for d in data]
        coverages = [d['coverage'] for d in data]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create horizontal bar chart
        bars = ax.barh(areas, coverages, color='skyblue', edgecolor='navy')

        # Customize chart
        ax.set_xlabel('Coverage (%)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(0, 100)

        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}%',
                   ha='left', va='center', fontsize=10)

        # Add grid
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Tight layout
        plt.tight_layout()

        # Save figure
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_trend(
        self,
        data: List[Dict[str, Any]],
        title: str = "Coverage Trend Over Time",
        filename: str = "trend.png"
    ) -> Path:
        """
        Create line chart showing coverage trend over time.

        Args:
            data: List of dicts with 'year' and 'coverage' keys
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart file
        """
        # Extract data
        years = [d['year'] for d in data]
        coverages = [d['coverage'] for d in data]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Create line chart
        ax.plot(years, coverages, marker='o', linewidth=2, markersize=8,
               color='darkblue', markerfacecolor='lightblue', markeredgewidth=2)

        # Customize chart
        ax.set_xlabel('Financial Year', fontsize=12)
        ax.set_ylabel('Coverage (%)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')

        # Add value labels on points
        for x, y in zip(years, coverages):
            ax.text(x, y + 1.5, f'{y:.1f}%', ha='center', va='bottom', fontsize=9)

        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')

        # Tight layout
        plt.tight_layout()

        # Save figure
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_summary(
        self,
        stats: Dict[str, Any],
        title: str = "Summary Statistics",
        filename: str = "summary.png"
    ) -> Path:
        """
        Create bar chart showing summary statistics.

        Args:
            stats: Dict with 'mean', 'min', 'max', 'count' keys
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart file
        """
        # Prepare data
        labels = ['Mean', 'Min', 'Max']
        values = [stats['mean'], stats['min'], stats['max']]
        colors = ['skyblue', 'lightcoral', 'lightgreen']

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6))

        # Create bar chart
        bars = ax.bar(labels, values, color=colors, edgecolor='black', linewidth=1.5)

        # Customize chart
        ax.set_ylabel('Coverage (%)', fontsize=12)
        ax.set_title(f'{title}\n(n={stats["count"]} areas)', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Add grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Tight layout
        plt.tight_layout()

        # Save figure
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_distribution(
        self,
        data: List[Dict[str, Any]],
        title: str = "Coverage Distribution",
        filename: str = "distribution.png"
    ) -> Path:
        """
        Create histogram showing distribution of coverage values.

        Args:
            data: List of dicts with 'coverage' key
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart file
        """
        # Extract coverage values
        coverages = [d['coverage'] for d in data]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create histogram
        n, bins, patches = ax.hist(coverages, bins=20, color='steelblue',
                                   edgecolor='black', alpha=0.7)

        # Customize chart
        ax.set_xlabel('Coverage (%)', fontsize=12)
        ax.set_ylabel('Number of Areas', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add statistics text box
        mean_val = sum(coverages) / len(coverages)
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}%')

        # Add legend
        ax.legend(fontsize=10)

        # Add grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Tight layout
        plt.tight_layout()

        # Save figure
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_table_comparison(
        self,
        data: List[Dict[str, Any]],
        selected_vaccines: List[str] = None,
        title: str = "Vaccine Coverage Comparison",
        filename: str = "table_comparison.png"
    ) -> Path:
        """
        Create grouped bar chart comparing vaccine coverage across geographic areas.

        Args:
            data: List of table rows with geographic_area and coverage columns
            selected_vaccines: List of vaccine column names to include (e.g., ['coverage_at_12_months_dtap_ipv_hib'])
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart file
        """
        import numpy as np
        
        if not data or not selected_vaccines:
            raise ValueError("Data and selected vaccines must be provided")
        
        # Extract geographic areas
        areas = [row.get('geographic_area', row.get('local_authority', 'Unknown')) for row in data]
        
        # Prepare vaccine data
        vaccine_data = {}
        vaccine_labels = []
        
        for vaccine_col in selected_vaccines:
            # Extract vaccine name from column for label
            if 'coverage_at_12_months_' in vaccine_col:
                vaccine_name = vaccine_col.replace('coverage_at_12_months_', '').replace('_', '/').upper()
            elif 'coverage_at_24_months_' in vaccine_col:
                vaccine_name = vaccine_col.replace('coverage_at_24_months_', '').replace('_', '/').upper()
            elif 'coverage_at_5_years_' in vaccine_col:
                vaccine_name = vaccine_col.replace('coverage_at_5_years_', '').replace('_', '/').upper()
            else:
                vaccine_name = vaccine_col.replace('coverage_', '').replace('_', '/').upper()
            
            vaccine_labels.append(vaccine_name)
            vaccine_data[vaccine_name] = [row.get(vaccine_col, 0) for row in data]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set up bar positions
        x = np.arange(len(areas))
        width = 0.8 / len(vaccine_labels)  # Width of bars
        
        # Create grouped bars
        colors = plt.cm.Set3(np.linspace(0, 1, len(vaccine_labels)))
        
        for i, (vaccine_name, values) in enumerate(vaccine_data.items()):
            offset = (i - len(vaccine_labels)/2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=vaccine_name, 
                         color=colors[i], edgecolor='black', linewidth=0.5)
            
            # Add value labels on bars (only if there's space)
            if len(areas) <= 5:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                               f'{height:.1f}%',
                               ha='center', va='bottom', fontsize=8)
        
        # Customize chart
        ax.set_xlabel('Geographic Area', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(areas, rotation=45, ha='right')
        ax.set_ylim(0, 105)
        ax.legend(loc='upper right', fontsize=9)
        
        # Add grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Tight layout
        plt.tight_layout()
        
        # Save figure
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath

    def plot_column_averages(
        self,
        data: List[Dict[str, Any]],
        selected_vaccines: List[str] = None,
        title: str = "Average Vaccine Coverage",
        filename: str = "column_averages.png"
    ) -> Path:
        """
        Create bar chart showing average coverage for selected vaccines.

        Args:
            data: List of table rows
            selected_vaccines: List of vaccine column names
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart file
        """
        import numpy as np
        
        if not data or not selected_vaccines:
            raise ValueError("Data and selected vaccines must be provided")
            
        # Calculate averages
        averages = []
        labels = []
        
        for col in selected_vaccines:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if values:
                avg = sum(values) / len(values)
                averages.append(avg)
                
                # Format label
                if 'coverage_at_12_months_' in col:
                    label = col.replace('coverage_at_12_months_', '').replace('_', '/').upper()
                elif 'coverage_at_24_months_' in col:
                    label = col.replace('coverage_at_24_months_', '').replace('_', '/').upper()
                elif 'coverage_at_5_years_' in col:
                    label = col.replace('coverage_at_5_years_', '').replace('_', '/').upper()
                else:
                    label = col.replace('coverage_', '').replace('_', '/').upper()
                labels.append(label)
        
        if not averages:
            raise ValueError("No valid data found for selected vaccines")

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bars
        x = np.arange(len(labels))
        bars = ax.bar(x, averages, color='skyblue', edgecolor='navy', alpha=0.7)
        
        # Customize chart
        ax.set_ylabel('Average Coverage (%)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylim(0, 105)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Tight layout
        plt.tight_layout()
        
        # Save figure
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath

    # High-level orchestration (for frontend chart generation)
    def generate_table_comparison_chart(
        self,
        table_type: str,
        cohort_name: str,
        year: int,
        selected_areas: List[str],
        selected_vaccines: List[str],
        table_builder,  # Dependency injection
        analyzer  # Dependency injection  
    ) -> Path:
        """
        Generate comparison chart from table data.
        
        This method orchestrates the complete workflow:
        - Retrieves table data via table_builder
        - Filters to selected areas using analyzer
        - Validates vaccine data
        - Selects appropriate chart type based on data size
        - Generates and returns chart
        
        Args:
            table_type: Type of table ('table1' or 'table4')
            cohort_name: Age cohort (e.g., '12 months', '24 months')
            year: Financial year (e.g., 2024)
            selected_areas: List of geographic area names to include
            selected_vaccines: List of vaccine column names to visualize
            table_builder: TableBuilder instance for data retrieval
            analyzer: VaccinationAnalyzer instance for filtering
            
        Returns:
            Path to generated chart file
            
        Raises:
            ValueError: If invalid table type, no data, or invalid vaccines
            
        Example:
            >>> chart_path = visualizer.generate_table_comparison_chart(
            ...     table_type='table1',
            ...     cohort_name='12 months',
            ...     year=2024,
            ...     selected_areas=['England', 'Wales'],
            ...     selected_vaccines=['coverage_at_12_months_dtap_ipv_hib'],
            ...     table_builder=table_builder,
            ...     analyzer=analyzer
            ... )
        """
        # Get table data
        if table_type == 'table1':
            table_data = table_builder.get_table1_uk_by_country(cohort_name=cohort_name, year=year)
            rows = table_data.get('data', [])
        elif table_type == 'table4':
            rows = table_builder.get_utla_table(cohort_name=cohort_name, year=year)
        else:
            raise ValueError(f"Unsupported table type: {table_type}")
        
        if not rows:
            raise ValueError("No table data found")
        
        # Filter to selected areas using analyzer
        if selected_areas:
            # Build filter dict with both possible column names
            filters = {}
            # Check which column exists in the data
            if rows and 'geographic_area' in rows[0]:
                filters['geographic_area'] = selected_areas
            if rows and 'local_authority' in rows[0]:
                filters['local_authority'] = selected_areas
            
            if filters:
                rows = analyzer.filter_table_data(rows, filters)
        
        if not rows:
            raise ValueError("No data for selected areas")
        
        if not selected_vaccines:
            raise ValueError("Please select at least one vaccine to visualize")
        
        # Clean data (replace None with 0 to prevent math errors)
        rows = self._clean_vaccine_data(rows, selected_vaccines)
        
        # Validate vaccines have data
        vaccines_with_data = self._filter_vaccines_with_data(rows, selected_vaccines)
        
        if not vaccines_with_data:
            raise ValueError("No vaccine data available to visualize")
        
        # Choose appropriate chart type based on data size
        if len(rows) > 10:
            # Use average comparison for large datasets
            return self.plot_column_averages(
                rows,
                selected_vaccines=vaccines_with_data,
                title=f"Average Vaccine Coverage (All Areas) - {cohort_name}",
                filename=f"table_comparison_{table_type}_{cohort_name.replace(' ', '_')}.png"
            )
        else:
            # Use detailed comparison for small datasets (filtered areas or Table 1)
            return self.plot_table_comparison(
                rows,
                selected_vaccines=vaccines_with_data,
                title=f"Vaccine Coverage Comparison - {cohort_name}",
                filename=f"table_comparison_{table_type}_{cohort_name.replace(' ', '_')}.png"
            )

    def _clean_vaccine_data(self, rows: List[Dict[str, Any]], vaccines: List[str]) -> List[Dict[str, Any]]:
        """
        Replace None values with 0 to prevent math errors.
        
        Args:
            rows: List of table rows
            vaccines: List of vaccine column names
            
        Returns:
            Cleaned rows with None replaced by 0
        """
        for row in rows:
            for vaccine_col in vaccines:
                if row.get(vaccine_col) is None:
                    row[vaccine_col] = 0
        return rows

    def _filter_vaccines_with_data(self, rows: List[Dict[str, Any]], vaccines: List[str]) -> List[str]:
        """
        Return only vaccines that have actual data (not all zeros).
        
        Args:
            rows: List of table rows
            vaccines: List of vaccine column names
            
        Returns:
            List of vaccine column names that have non-zero data
        """
        vaccines_with_data = []
        for vaccine_col in vaccines:
            has_data = any(row.get(vaccine_col, 0) > 0 for row in rows)
            if has_data:
                vaccines_with_data.append(vaccine_col)
        return vaccines_with_data
