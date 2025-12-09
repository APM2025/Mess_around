"""
Demo script showing user logging and CSV export capabilities.

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
from src.user_log import UserActivityLogger
from src.export import DataExporter


def main():
    """Demonstrate logging and export capabilities."""
    try:
        # Setup
        session = get_session()
        analyzer = VaccinationAnalyzer(session)
        logger = UserActivityLogger(Path("logs/demo_activity.log"))
        exporter = DataExporter()

        print("=" * 70)
        print("USER LOGGING AND EXPORT DEMO")
        print("=" * 70)

        # Part 1: User Activity Logging
        print("\n[PART 1] USER ACTIVITY LOGGING")
        print("-" * 70)

        print("\n1. Logging query operations:")
        logger.log_action("query", "filter_data", "vaccine_code=MMR1, cohort=24 months")
        print("   Logged: Query for MMR1 data")

        logger.log_action("query", "get_summary", "149 records")
        print("   Logged: Summary statistics calculation")

        logger.log_action("query", "get_top_areas", "n=10")
        print("   Logged: Top areas query")

        print("\n2. Retrieving recent logs:")
        recent = logger.get_recent_logs(n=3)
        for i, log in enumerate(recent, 1):
            print(f"   {i}. {log}")

        print("\n3. Getting log summary:")
        summary = logger.get_log_summary()
        print(f"   Total actions logged: {summary['total']}")
        for action_type, count in summary.items():
            if action_type != 'total':
                print(f"   {action_type.upper()}: {count}")

        # Part 2: Data Export
        print("\n\n[PART 2] CSV DATA EXPORT")
        print("-" * 70)

        print("\n4. Querying MMR1 data:")
        data = analyzer.filter_data(vaccine_code='MMR1', cohort_name='24 months')
        print(f"   Retrieved {len(data)} records")
        logger.log_action("query", "filter_data", f"vaccine_code=MMR1, records={len(data)}")

        print("\n5. Exporting top 20 areas to CSV:")
        top_20 = analyzer.get_top_areas('MMR1', n=20, cohort_name='24 months')
        output_dir = project_root / "output" / "exports"
        output_file = output_dir / "top_20_mmr1_coverage.csv"

        result = exporter.export_to_csv(top_20, output_file)
        print(f"   Exported to: {result}")
        print(f"   File size: {result.stat().st_size} bytes")
        logger.log_action("export", "csv", f"file={result.name}, rows={len(top_20)}")

        print("\n6. Exporting summary statistics:")
        summary_stats = analyzer.get_summary(data)
        summary_export = [
            {'statistic': 'count', 'value': summary_stats['count']},
            {'statistic': 'mean', 'value': summary_stats['mean']},
            {'statistic': 'min', 'value': summary_stats['min']},
            {'statistic': 'max', 'value': summary_stats['max']},
        ]

        summary_file = output_dir / "mmr1_summary_stats.csv"
        exporter.export_to_csv(summary_export, summary_file)
        print(f"   Exported to: {summary_file}")
        logger.log_action("export", "csv", f"file={summary_file.name}, rows=4")

        print("\n7. Exporting trend data:")
        trend = analyzer.get_trend('MMR1', cohort_name='24 months')
        trend_file = output_dir / "mmr1_trend_data.csv"
        exporter.export_to_csv(trend, trend_file)
        print(f"   Exported to: {trend_file}")
        print(f"   Years covered: {len(trend)}")
        logger.log_action("export", "csv", f"file={trend_file.name}, rows={len(trend)}")

        # Part 3: Final Summary
        print("\n\n[PART 3] FINAL SUMMARY")
        print("-" * 70)

        print("\n8. All exported files:")
        if output_dir.exists():
            for csv_file in sorted(output_dir.glob("*.csv")):
                size_kb = csv_file.stat().st_size / 1024
                print(f"   - {csv_file.name} ({size_kb:.1f} KB)")

        print("\n9. Complete activity log:")
        all_logs = logger.get_all_logs()
        print(f"   Total actions logged in this session: {len(all_logs)}")
        print("   Last 5 actions:")
        for log in logger.get_recent_logs(n=5):
            print(f"   {log}")

        print("\n" + "=" * 70)
        print("DEMO COMPLETE!")
        print("=" * 70)
        print("\nSuccessfully demonstrated:")
        print("  - User activity logging with timestamps")
        print("  - Log querying and filtering")
        print("  - CSV export of filtered data")
        print("  - Multiple export formats (top areas, summary, trends)")
        print(f"\nLog file: {logger.log_file}")
        print(f"Export directory: {output_dir}")
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
