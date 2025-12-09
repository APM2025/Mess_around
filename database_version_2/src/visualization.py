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
