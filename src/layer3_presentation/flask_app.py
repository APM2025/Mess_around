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

# Add project to path (we're in src/layer3_presentation, need to go up 2 levels)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.layer1_database.database import get_session
from src.layer2_business_logic.fs_analysis import VaccinationAnalyzer
from src.layer3_presentation.visualization import VaccinationVisualizer
from src.layer2_business_logic.crud import VaccinationCRUD
from src.layer2_business_logic.export import DataExporter
from src.layer2_business_logic.user_log import UserActivityLogger
from src.layer2_business_logic.table_builder import TableBuilder
from src.layer1_database.models import GeographicArea, Vaccine, AgeCohort, FinancialYear, LocalAuthorityCoverage, NationalCoverage

# Initialize Flask app (template folder is at project root)
app = Flask(__name__, template_folder=str(project_root / 'templates'))
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize services
session = get_session()
analyzer = VaccinationAnalyzer(session)
visualizer = VaccinationVisualizer(output_dir=project_root / "static/charts")
crud = VaccinationCRUD(session)
exporter = DataExporter()
logger = UserActivityLogger(project_root / "logs/web_activity.log")
table_builder = TableBuilder(session)


@app.route('/')
def index():
    """Main dashboard page - ODS tables."""
    logger.log_action("view", "dashboard", "ods_tables")
    return render_template('ods_tables.html')


@app.route('/ods_tables')
def ods_tables():
    """Render ODS tables page."""
    logger.log_action("page_load", "ods_tables", "table_view")
    return render_template('ods_tables.html')


@app.route('/api/reload-data', methods=['POST'])
def reload_data():
    """Reload original data from CSV files using dataloader module."""
    try:
        logger.log_action("admin", "reload_data", "starting")
        
        # Use the database reload service
        from src.layer2_business_logic.database_reload import reload_all_data
        
        # Get session and reload all data
        result = reload_all_data(session, verbose=False)
        
        logger.log_action("admin", "reload_data", "completed")
        return jsonify({
            'message': 'Database reloaded successfully',
            'status': 'success',
            'summary': result
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.log_action("error", "reload_data", str(e))
        print(f"RELOAD ERROR: {error_trace}")
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500




@app.route('/logs')
def activity_logs():
    """Activity logs dashboard."""
    logger.log_action("view", "dashboard", "activity_logs")
    return render_template('activity_logs.html')








@app.route('/api/areas', methods=['GET'])
def get_areas():
    """Get all available areas for selection."""
    # Delegate to CRUD layer instead of direct database query
    areas = crud.get_areas_by_type_as_dicts('utla')
    return jsonify(areas)





@app.route('/api/visualize/table-comparison', methods=['POST'])
def visualize_table_comparison():
    """Generate comparison chart from table data."""
    try:
        data = request.json
        table_type = data.get('table_type', 'table1')
        cohort_name = data.get('cohort_name', '12 months')
        year = data.get('year', 2024)
        selected_areas = data.get('selected_areas', [])
        selected_vaccines = data.get('selected_vaccines', [])

        logger.log_action("visualize", "table_comparison", 
                         f"table={table_type}, areas={len(selected_areas)}, vaccines={len(selected_vaccines)}")

        # Delegate all logic to visualization service
        chart_path = visualizer.generate_table_comparison_chart(
            table_type=table_type,
            cohort_name=cohort_name,
            year=year,
            selected_areas=selected_areas,
            selected_vaccines=selected_vaccines,
            table_builder=table_builder,
            analyzer=analyzer
        )

        return jsonify({'chart_url': f"/static/charts/{chart_path.name}"})

    except ValueError as e:
        # Application errors (expected - invalid input, no data, etc.)
        logger.log_action("error", "viz_table_comparison", str(e))
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Unexpected errors
        import traceback
        error_trace = traceback.format_exc()
        logger.log_action("error", "viz_table_comparison", str(e))
        print(f"VISUALIZATION ERROR: {error_trace}")  # Print to console for debugging
        return jsonify({'error': 'Internal server error'}), 500


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


@app.route('/api/crud/coverage', methods=['POST', 'DELETE'])
def manage_coverage():
    """CRUD operations for coverage records."""
    if request.method == 'POST':
        data = request.json
        
        logger.log_action("update", "coverage", f"area={data.get('area_code')}, vaccine={data.get('vaccine_code')}")
        
        try:
            # Delegate to CRUD service
            result = crud.upsert_coverage_by_codes(
                area_code=data['area_code'],
                vaccine_code=data['vaccine_code'],
                cohort_name=data.get('cohort_name', '24 months'),
                year=data.get('year', 2024),
                eligible_population=data.get('eligible_population'),
                vaccinated_count=data.get('vaccinated_count'),
                coverage_percentage=data.get('coverage_percentage')
            )
            return jsonify({'message': 'Record saved', 'id': result.coverage_id})
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    elif request.method == 'DELETE':
        data = request.json
        logger.log_action("delete", "coverage", f"area={data.get('area_code')}, vaccine={data.get('vaccine_code')}")
        
        try:
            # Delegate to CRUD service
            deleted = crud.delete_coverage_by_codes(
                area_code=data['area_code'],
                vaccine_code=data['vaccine_code'],
                cohort_name=data.get('cohort_name', '24 months'),
                year=data.get('year', 2024)
            )
            
            if deleted:
                return jsonify({'message': 'Record deleted'})
            else:
                return jsonify({'error': 'Record not found'}), 404
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400


@app.route('/api/tables/utla', methods=['POST'])
def get_utla_table():
    """Get UTLA coverage table with optional server-side filtering."""
    data = request.json
    cohort_name = data.get('cohort_name', '24 months')
    year = data.get('year', 2024)
    filters = data.get('filters', {})  # NEW: Accept filter parameters

    logger.log_action("query", "utla_table", f"cohort={cohort_name}, year={year}, filters={len(filters)} columns")

    table_data = table_builder.get_utla_table(cohort_name=cohort_name, year=year)
    
    # Apply server-side filtering using analyzer module
    if filters and table_data:
        filtered_data = analyzer.filter_table_data(
            table_data=table_data,
            filters=filters
        )
        logger.log_action("filter", "utla_backend_filter", f"Filtered to {len(filtered_data)} of {len(table_data)} rows")
    else:
        filtered_data = table_data

    return jsonify({
        'title': f'Table 4. Completed primary immunisations in children aged {cohort_name} in England by UTLA',
        'notes': [
            '[z] not applicable',
            '[note 18] City of London is included in Hackney.',
            '[note 19] Isles of Scilly is included in Cornwall.',
            '[note 23] Please note that system changes in 14 UTLAs in London earlier this year...'
        ],
        'cohort': cohort_name,
        'year': year,
        'row_count': len(filtered_data),
        'total_rows': len(table_data),
        'filtered': bool(filters),
        'data': filtered_data
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


@app.route('/api/crud/row', methods=['POST', 'DELETE'])
def manage_row():
    """CRUD operations for entire rows (multiple vaccines)."""
    if request.method == 'POST':
        data = request.json
        area_code = data.get('area_code')
        year_val = data.get('year', 2024)
        cohort_name = data.get('cohort_name', '24 months')
        updates = data.get('vaccine_data', [])
        
        logger.log_action("update", "row", f"area={area_code}, updates={len(updates)}")
        
        try:
            # Delegate all business logic to CRUD service
            count = crud.update_row_vaccines(
                area_code=area_code,
                cohort_name=cohort_name,
                year=year_val,
                vaccine_updates=updates
            )
            
            return jsonify({'message': f'Updated {count} records'})
            
        except ValueError as e:
            # Application errors (invalid data)
            logger.log_action("error", "row_update", str(e))
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            # Unexpected errors
            logger.log_action("error", "row_update", str(e))
            return jsonify({'error': str(e)}), 500

    elif request.method == 'DELETE':
        data = request.json
        area_code = data.get('area_code')
        year_val = data.get('year', 2024)
        cohort_name = data.get('cohort_name', '24 months')
        
        logger.log_action("delete", "row", f"area={area_code}")
        
        try:
            # Delegate all business logic to CRUD layer
            count = crud.delete_row_by_codes(
                area_code=area_code,
                cohort_name=cohort_name,
                year=year_val
            )
            return jsonify({'message': f'Deleted {count} records'})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
@app.route('/api/tables/table1', methods=['POST'])
def get_table1():
    """Get Table 1: UK by country, with optional server-side filtering."""
    data = request.json
    cohort_name = data.get('cohort_name', '12 months')
    year = data.get('year', 2024)
    filters = data.get('filters', {})  # NEW: Accept filter parameters

    logger.log_action("query", "table1_uk_by_country", f"cohort={cohort_name}, year={year}, filters={len(filters)} columns")

    try:
        result = table_builder.get_table1_uk_by_country(cohort_name=cohort_name, year=year)
        
        # Apply server-side filtering using analyzer module
        if filters and result.get('data'):
            filtered_data = analyzer.filter_table_data(
                table_data=result['data'],
                filters=filters
            )
            result['data'] = filtered_data
            result['filtered'] = True
            result['filter_count'] = len(filters)
            logger.log_action("filter", "table1_backend_filter", f"Filtered {len(result['data'])} rows")
        
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"TABLE1 ERROR: {traceback.format_exc()}")
        logger.log_action("error", "table1", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/tables/hepb', methods=['POST'])
def get_hepb_table():
    """Get Table 7: Neonatal Hepatitis B coverage by UTLA."""
    data = request.json
    year = data.get('year', 2024)

    logger.log_action("query", "hepb_table", f"year={year}")

    result = table_builder.get_hepb_table(year=year)

    return jsonify(result)


@app.route('/api/tables/bcg', methods=['POST'])
def get_bcg_table():
    """Get Table 8: BCG vaccine coverage by UTLA."""
    data = request.json
    year = data.get('year', 2024)

    logger.log_action("query", "bcg_table", f"year={year}")

    result = table_builder.get_bcg_table(year=year)

    return jsonify(result)


@app.route('/api/all-areas', methods=['GET'])
def get_all_areas():
    """Get all geographic areas for CRUD dropdown."""
    # Delegate to CRUD layer instead of direct database query
    areas = crud.get_all_areas_as_dicts()
    return jsonify(areas)


if __name__ == '__main__':
    # Create necessary directories
    (project_root / "static/charts").mkdir(parents=True, exist_ok=True)
    (project_root / "static/exports").mkdir(parents=True, exist_ok=True)
    (project_root / "logs").mkdir(parents=True, exist_ok=True)

    app.run(debug=True, port=5000)
