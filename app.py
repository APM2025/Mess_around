"""
Flask Web Application for Vaccination Coverage Dashboard

This application provides a comprehensive web interface for:
- Data analysis and filtering
- Interactive visualizations
- CRUD operations
- CSV exports
- Activity logging
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from pathlib import Path
import sys
import io
import base64

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database_version_2.src.database import get_session
from database_version_2.src.fs_analysis import VaccinationAnalyzer
from database_version_2.src.visualization import VaccinationVisualizer
from database_version_2.src.crud import VaccinationCRUD
from database_version_2.src.export import DataExporter
from database_version_2.src.user_log import UserActivityLogger
from database_version_2.src.table_builder import TableBuilder

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize services
session = get_session()
analyzer = VaccinationAnalyzer(session)
visualizer = VaccinationVisualizer(output_dir=Path("static/charts"))
crud = VaccinationCRUD(session)
exporter = DataExporter()
logger = UserActivityLogger(Path("logs/web_activity.log"))
table_builder = TableBuilder(session)


@app.route('/')
def index():
    """Main dashboard page - ODS tables."""
    logger.log_action("view", "dashboard", "ods_tables")
    return render_template('ods_tables.html')

@app.route('/tables')
def table_dashboard():
    """Table view dashboard."""
    logger.log_action("view", "dashboard", "table_view")
    return render_template('table_dashboard.html')

@app.route('/charts')
def charts_dashboard():
    """Charts and visualizations dashboard."""
    logger.log_action("view", "dashboard", "charts_view")
    return render_template('dashboard.html')


@app.route('/api/vaccines')
def get_vaccines():
    """Get list of all vaccines."""
    logger.log_action("query", "get_vaccines", "api_call")
    vaccines = crud.get_all_vaccines()
    return jsonify([
        {'vaccine_code': v.vaccine_code, 'vaccine_name': v.vaccine_name}
        for v in vaccines
    ])


@app.route('/api/filter', methods=['POST'])
def filter_data():
    """Filter vaccination data."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("query", "filter_data", f"vaccine={vaccine_code}, cohort={cohort_name}")

    results = analyzer.filter_data(
        vaccine_code=vaccine_code,
        cohort_name=cohort_name
    )

    return jsonify({
        'count': len(results),
        'data': results[:100]  # Limit to first 100 for performance
    })


@app.route('/api/summary', methods=['POST'])
def get_summary():
    """Get summary statistics."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("query", "get_summary", f"vaccine={vaccine_code}")

    filtered_data = analyzer.filter_data(
        vaccine_code=vaccine_code,
        cohort_name=cohort_name
    )

    if not filtered_data:
        return jsonify({'error': 'No data found'}), 404

    summary = analyzer.get_summary(filtered_data)
    return jsonify(summary)


@app.route('/api/top-areas', methods=['POST'])
def get_top_areas():
    """Get top performing areas."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    n = data.get('n', 10)
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("query", "get_top_areas", f"vaccine={vaccine_code}, n={n}")

    top_areas = analyzer.get_top_areas(
        vaccine_code=vaccine_code,
        n=n,
        cohort_name=cohort_name
    )

    return jsonify(top_areas)


@app.route('/api/trend', methods=['POST'])
def get_trend():
    """Get coverage trend over time."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("query", "get_trend", f"vaccine={vaccine_code}")

    trend = analyzer.get_trend(
        vaccine_code=vaccine_code,
        cohort_name=cohort_name
    )

    return jsonify(trend)


@app.route('/api/visualize/top-areas', methods=['POST'])
def visualize_top_areas():
    """Generate top areas chart."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    n = data.get('n', 10)
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("visualize", "top_areas", f"vaccine={vaccine_code}")

    top_areas = analyzer.get_top_areas(vaccine_code, n, cohort_name)

    if not top_areas:
        return jsonify({'error': 'No data found'}), 404

    chart_path = visualizer.plot_top_areas(
        top_areas,
        title=f"Top {n} Areas - {vaccine_code}",
        filename=f"top_areas_{vaccine_code}.png"
    )

    return jsonify({
        'chart_url': f"/static/charts/{chart_path.name}"
    })


@app.route('/api/visualize/trend', methods=['POST'])
def visualize_trend():
    """Generate trend chart."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("visualize", "trend", f"vaccine={vaccine_code}")

    trend = analyzer.get_trend(vaccine_code, cohort_name)

    if not trend:
        return jsonify({'error': 'No data found'}), 404

    chart_path = visualizer.plot_trend(
        trend,
        title=f"{vaccine_code} Coverage Trend",
        filename=f"trend_{vaccine_code}.png"
    )

    return jsonify({
        'chart_url': f"/static/charts/{chart_path.name}"
    })


@app.route('/api/visualize/summary', methods=['POST'])
def visualize_summary():
    """Generate summary statistics chart."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("visualize", "summary", f"vaccine={vaccine_code}")

    filtered_data = analyzer.filter_data(vaccine_code, cohort_name=cohort_name)

    if not filtered_data:
        return jsonify({'error': 'No data found'}), 404

    summary = analyzer.get_summary(filtered_data)

    chart_path = visualizer.plot_summary(
        summary,
        title=f"{vaccine_code} Summary Statistics",
        filename=f"summary_{vaccine_code}.png"
    )

    return jsonify({
        'chart_url': f"/static/charts/{chart_path.name}"
    })


@app.route('/api/visualize/distribution', methods=['POST'])
def visualize_distribution():
    """Generate distribution chart."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("visualize", "distribution", f"vaccine={vaccine_code}")

    filtered_data = analyzer.filter_data(vaccine_code, cohort_name=cohort_name)

    if not filtered_data:
        return jsonify({'error': 'No data found'}), 404

    chart_path = visualizer.plot_distribution(
        filtered_data,
        title=f"{vaccine_code} Coverage Distribution",
        filename=f"distribution_{vaccine_code}.png"
    )

    return jsonify({
        'chart_url': f"/static/charts/{chart_path.name}"
    })


@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export filtered data to CSV."""
    data = request.json
    vaccine_code = data.get('vaccine_code')
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("export", "csv", f"vaccine={vaccine_code}")

    filtered_data = analyzer.filter_data(vaccine_code, cohort_name=cohort_name)

    if not filtered_data:
        return jsonify({'error': 'No data found'}), 404

    # Export to temp file
    export_dir = Path("static/exports")
    export_file = export_dir / f"{vaccine_code}_export.csv"

    exporter.export_to_csv(filtered_data, export_file)

    return jsonify({
        'download_url': f"/static/exports/{export_file.name}",
        'row_count': len(filtered_data)
    })


@app.route('/api/logs/recent')
def get_recent_logs():
    """Get recent activity logs."""
    n = request.args.get('n', 20, type=int)
    logs = logger.get_recent_logs(n=n)
    return jsonify({'logs': logs})


@app.route('/api/logs/summary')
def get_log_summary():
    """Get log summary statistics."""
    summary = logger.get_log_summary()
    return jsonify(summary)


@app.route('/api/crud/vaccines', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_vaccines():
    """CRUD operations for vaccines."""
    if request.method == 'GET':
        vaccines = crud.get_all_vaccines()
        return jsonify([
            {'vaccine_code': v.vaccine_code, 'vaccine_name': v.vaccine_name}
            for v in vaccines
        ])

    elif request.method == 'POST':
        data = request.json
        logger.log_action("create", "vaccine", f"code={data.get('vaccine_code')}")
        vaccine = crud.create_vaccine(
            vaccine_code=data['vaccine_code'],
            vaccine_name=data['vaccine_name']
        )
        return jsonify({
            'vaccine_code': vaccine.vaccine_code,
            'vaccine_name': vaccine.vaccine_name
        }), 201

    elif request.method == 'PUT':
        data = request.json
        logger.log_action("update", "vaccine", f"code={data.get('vaccine_code')}")
        vaccine = crud.update_vaccine(
            vaccine_code=data['vaccine_code'],
            vaccine_name=data['vaccine_name']
        )
        if vaccine:
            return jsonify({
                'vaccine_code': vaccine.vaccine_code,
                'vaccine_name': vaccine.vaccine_name
            })
        return jsonify({'error': 'Vaccine not found'}), 404

    elif request.method == 'DELETE':
        data = request.json
        logger.log_action("delete", "vaccine", f"code={data.get('vaccine_code')}")
        success = crud.delete_vaccine(data['vaccine_code'])
        if success:
            return jsonify({'message': 'Vaccine deleted'})
        return jsonify({'error': 'Vaccine not found'}), 404


@app.route('/api/tables/utla', methods=['POST'])
def get_utla_table():
    """Get UTLA coverage table in original ODS format."""
    data = request.json
    cohort_name = data.get('cohort_name', '24 months')
    year = data.get('year', 2024)

    logger.log_action("query", "utla_table", f"cohort={cohort_name}, year={year}")

    table_data = table_builder.get_utla_table(cohort_name=cohort_name, year=year)

    return jsonify({
        'cohort': cohort_name,
        'year': year,
        'row_count': len(table_data),
        'data': table_data
    })


@app.route('/api/tables/regional', methods=['POST'])
def get_regional_table():
    """Get regional time series table."""
    data = request.json
    cohort_name = data.get('cohort_name', '24 months')

    logger.log_action("query", "regional_table", f"cohort={cohort_name}")

    table_data = table_builder.get_regional_table(cohort_name=cohort_name)

    return jsonify({
        'cohort': cohort_name,
        'row_count': len(table_data),
        'data': table_data
    })


@app.route('/api/tables/england-summary', methods=['POST'])
def get_england_summary_table():
    """Get England summary statistics."""
    data = request.json
    cohort_name = data.get('cohort_name', '24 months')
    year = data.get('year', 2024)

    logger.log_action("query", "england_summary", f"cohort={cohort_name}, year={year}")

    summary = table_builder.get_england_summary(cohort_name=cohort_name, year=year)

    return jsonify(summary)


@app.route('/api/tables/table1', methods=['POST'])
def get_table1():
    """Get Table 1: UK by country, 12 months cohort."""
    data = request.json
    cohort_name = data.get('cohort_name', '12 months')
    year = data.get('year', 2024)

    logger.log_action("query", "table1_uk_by_country", f"cohort={cohort_name}, year={year}")

    result = table_builder.get_table1_uk_by_country(cohort_name=cohort_name, year=year)

    return jsonify(result)


if __name__ == '__main__':
    # Create necessary directories
    Path("static/charts").mkdir(parents=True, exist_ok=True)
    Path("static/exports").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)

    app.run(debug=True, port=5000)
