"""
Demo script showing all visualization capabilities with real data.

NOTE: This script requires a populated database at data/vaccination_coverage.db
Run create_database.py first to populate data before running this script.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_session
from src.fs_analysis import VaccinationAnalyzer
from src.visualization import VaccinationVisualizer


def main():
    """Create visualizations for MMR1 vaccination data."""
    try:
        # Setup
        session = get_session()
        analyzer = VaccinationAnalyzer(session)
        output_dir = project_root / "output" / "visualizations"
        visualizer = VaccinationVisualizer(output_dir=output_dir)

        print("=" * 70)
        print("VACCINATION DATA VISUALIZATION DEMO")
        print("=" * 70)

        # Get MMR1 data
        vaccine_code = 'MMR1'
        cohort_name = '24 months'

        print(f"\n[1/4] Generating top areas chart for {vaccine_code}...")
        top_areas = analyzer.get_top_areas(vaccine_code, n=10, cohort_name=cohort_name)
        if top_areas:
            filepath = visualizer.plot_top_areas(
                top_areas,
                title=f"Top 10 Areas - {vaccine_code} Coverage",
                filename=f"{vaccine_code}_top_areas.png"
            )
            print(f"    [OK] Saved: {filepath}")
        else:
            print("    [WARN] No data available for top areas chart")

        # Get summary statistics
        print(f"\n[2/4] Generating summary statistics chart for {vaccine_code}...")
        data = analyzer.filter_data(vaccine_code=vaccine_code, cohort_name=cohort_name)
        if data:
            summary = analyzer.get_summary(data)
            filepath = visualizer.plot_summary(
                summary,
                title=f"{vaccine_code} Coverage Summary",
                filename=f"{vaccine_code}_summary.png"
            )
            print(f"    [OK] Saved: {filepath}")
            print(f"    Stats: Mean={summary['mean']:.1f}%, Min={summary['min']:.1f}%, Max={summary['max']:.1f}%")
        else:
            print("    [WARN] No data available for summary chart")

        # Get trend data
        print(f"\n[3/4] Generating trend chart for {vaccine_code}...")
        trend = analyzer.get_trend(vaccine_code, cohort_name=cohort_name)
        if trend:
            filepath = visualizer.plot_trend(
                trend,
                title=f"{vaccine_code} Coverage Trend - England",
                filename=f"{vaccine_code}_trend.png"
            )
            print(f"    [OK] Saved: {filepath}")
            print(f"    Years covered: {trend[0]['year']} to {trend[-1]['year']}")
        else:
            print("    [WARN] No trend data available")

        # Get distribution
        print(f"\n[4/4] Generating distribution chart for {vaccine_code}...")
        if data:
            filepath = visualizer.plot_distribution(
                data,
                title=f"{vaccine_code} Coverage Distribution Across UTLAs",
                filename=f"{vaccine_code}_distribution.png"
            )
            print(f"    [OK] Saved: {filepath}")
            print(f"    Sample size: {len(data)} areas")
        else:
            print("    [WARN] No data available for distribution chart")

        print("\n" + "=" * 70)
        print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nCharts saved to: {output_dir}")
        print("\nGenerated files:")
        if output_dir.exists():
            for png_file in sorted(output_dir.glob("*.png")):
                print(f"  - {png_file.name}")
        print()

        session.close()

    except FileNotFoundError:
        print("ERROR: Database file not found.")
        print("Please run create_database.py first to populate the database.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
