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

from src.database import get_session
from src.fs_analysis import VaccinationAnalyzer
from src.visualization import VaccinationVisualizer
from src.crud import VaccinationCRUD
from src.export import DataExporter
from src.user_log import UserActivityLogger
from src.table_builder import TableBuilder
from src.models import GeographicArea, Vaccine, AgeCohort, FinancialYear, LocalAuthorityCoverage, NationalCoverage

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


@app.route('/api/visualize/compare-areas', methods=['POST'])
def visualize_compare_areas():
    """Generate area comparison chart."""
    data = request.json
    area_codes = data.get('area_codes', [])
    cohort_name = data.get('cohort_name', '24 months')
    year = data.get('year', 2024)

    logger.log_action("visualize", "compare_areas", f"areas={len(area_codes)}, cohort={cohort_name}")

    if not area_codes or len(area_codes) < 2:
        return jsonify({'error': 'Please select at least 2 areas to compare'}), 400

    # Get data for selected areas
    table_data = table_builder.get_utla_table(cohort_name=cohort_name, year=year)

    # Filter to selected areas
    selected_data = [row for row in table_data if row['code'] in area_codes]

    if not selected_data:
        return jsonify({'error': 'No data found for selected areas'}), 404

    chart_path = visualizer.plot_area_comparison(
        selected_data,
        cohort_name=cohort_name,
        title=f"Vaccine Coverage Comparison - {cohort_name}",
        filename=f"compare_areas_{cohort_name.replace(' ', '_')}.png"
    )

    return jsonify({
        'chart_url': f"/static/charts/{chart_path.name}"
    })


@app.route('/api/areas', methods=['GET'])
def get_areas():
    """Get all available areas for selection."""
    areas = session.query(GeographicArea).filter_by(area_type='utla').order_by(GeographicArea.area_name).all()

    return jsonify([{
        'code': area.area_code,
        'name': area.area_name
    } for area in areas])


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

        logger.log_action("visualize", "table_comparison", f"table={table_type}, areas={len(selected_areas)}")

        # Get table data
        if table_type == 'table1':
            table_data = table_builder.get_table1_uk_by_country(cohort_name=cohort_name, year=year)
            rows = table_data.get('data', [])
        elif table_type == 'table4':
            rows = table_builder.get_utla_table(cohort_name=cohort_name, year=year)
        else:
            return jsonify({'error': 'Unsupported table type'}), 400

        if not rows:
            return jsonify({'error': 'No table data found'}), 404

        # Filter to selected areas
        if selected_areas:
            rows = [row for row in rows if 
                    row.get('geographic_area') in selected_areas or 
                    row.get('local_authority') in selected_areas]

        if not rows:
            return jsonify({'error': 'No data for selected areas'}), 404

        if not selected_vaccines:
            return jsonify({'error': 'Please select at least one vaccine to visualize'}), 400

        # Replace None values with 0 to prevent math errors
        for row in rows:
            for vaccine_col in selected_vaccines:
                if row.get(vaccine_col) is None:
                    row[vaccine_col] = 0

        # Filter to only vaccines that have actual data (not all zeros)
        vaccines_with_data = []
        for vaccine_col in selected_vaccines:
            has_data = any(row.get(vaccine_col, 0) > 0 for row in rows)
            if has_data:
                vaccines_with_data.append(vaccine_col)
        
        if not vaccines_with_data:
            return jsonify({'error': 'No vaccine data available to visualize'}), 404
        
        selected_vaccines = vaccines_with_data

        # Generate chart
        if len(rows) > 10:
            # Use average comparison for large datasets (unless specific areas selected reduced it)
            chart_path = visualizer.plot_column_averages(
                rows,
                selected_vaccines=selected_vaccines,
                title=f"Average Vaccine Coverage (All Areas) - {cohort_name}",
                filename=f"table_comparison_{table_type}_{cohort_name.replace(' ', '_')}.png"
            )
        else:
            # Use detailed comparison for small datasets (filtered areas or Table 1)
            chart_path = visualizer.plot_table_comparison(
                rows,
                selected_vaccines=selected_vaccines,
                title=f"Vaccine Coverage Comparison - {cohort_name}",
                filename=f"table_comparison_{table_type}_{cohort_name.replace(' ', '_')}.png"
            )

        return jsonify({
            'chart_url': f"/static/charts/{chart_path.name}"
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.log_action("error", "viz_table_comparison", str(e))
        print(f"VISUALIZATION ERROR: {error_trace}")  # Print to console for debugging
        return jsonify({'error': str(e)}), 500


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
        
        # Log the action
        logger.log_action("update", "coverage", f"area={data.get('area_code')}, vaccine={data.get('vaccine_code')}")
        
        # Get IDs from codes/names
        year_obj = session.query(FinancialYear).filter_by(year_start=data.get('year', 2024)).first()
        cohort = session.query(AgeCohort).filter_by(cohort_name=data.get('cohort_name', '24 months')).first()
        vaccine = session.query(Vaccine).filter_by(vaccine_code=data.get('vaccine_code')).first()
        # Area code is passed directly as area_code
        
        if not all([year_obj, cohort, vaccine, data.get('area_code')]):
            return jsonify({'error': 'Invalid reference data provided'}), 400
            
        # Check if record exists
        existing = crud.get_coverage_by_keys(
            area_code=data['area_code'],
            vaccine_id=vaccine.vaccine_id,
            cohort_id=cohort.cohort_id,
            year_id=year_obj.year_id
        )
        
        if existing:
            # Update
            updated = crud.update_coverage_record(
                coverage_id=existing.coverage_id,
                eligible_population=data.get('eligible_population'),
                vaccinated_count=data.get('vaccinated_count'),
                coverage_percentage=data.get('coverage_percentage')
            )
            return jsonify({'message': 'Record updated', 'id': updated.coverage_id})
        else:
            # Create
            created = crud.create_coverage_record(
                area_code=data['area_code'],
                vaccine_id=vaccine.vaccine_id,
                cohort_id=cohort.cohort_id,
                year_id=year_obj.year_id,
                eligible_population=data.get('eligible_population'),
                vaccinated_count=data.get('vaccinated_count'),
                coverage_percentage=data.get('coverage_percentage')
            )
            return jsonify({'message': 'Record created', 'id': created.coverage_id})

    elif request.method == 'DELETE':
        data = request.json
        logger.log_action("delete", "coverage", f"area={data.get('area_code')}, vaccine={data.get('vaccine_code')}")
        
        # Get IDs
        year_obj = session.query(FinancialYear).filter_by(year_start=data.get('year', 2024)).first()
        cohort = session.query(AgeCohort).filter_by(cohort_name=data.get('cohort_name', '24 months')).first()
        vaccine = session.query(Vaccine).filter_by(vaccine_code=data.get('vaccine_code')).first()
        
        if not all([year_obj, cohort, vaccine, data.get('area_code')]):
            return jsonify({'error': 'Record not found (invalid refs)'}), 404
            
        existing = crud.get_coverage_by_keys(
            area_code=data['area_code'],
            vaccine_id=vaccine.vaccine_id,
            cohort_id=cohort.cohort_id,
            year_id=year_obj.year_id
        )
        
        if existing:
            crud.delete_coverage_record(existing.coverage_id)
            return jsonify({'message': 'Record deleted'})
        
        return jsonify({'error': 'Record not found'}), 404


@app.route('/api/tables/utla', methods=['POST'])
def get_utla_table():
    """Get UTLA coverage table in original ODS format."""
    data = request.json
    cohort_name = data.get('cohort_name', '24 months')
    year = data.get('year', 2024)

    logger.log_action("query", "utla_table", f"cohort={cohort_name}, year={year}")

    table_data = table_builder.get_utla_table(cohort_name=cohort_name, year=year)

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
        
        # Get References
        year_obj = session.query(FinancialYear).filter_by(year_start=year_val).first()
        cohort = session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        
        if not all([year_obj, cohort, area_code]):
            return jsonify({'error': 'Invalid reference data'}), 400

        success_count = 0
        
        # Determine which table to use based on area type
        area = session.query(GeographicArea).filter_by(area_code=area_code).first()
        if not area:
            return jsonify({'error': 'Area not found'}), 404
        
        # Table 1 uses NationalCoverage (country/UK), Table 4 uses LocalAuthorityCoverage (UTLA)
        is_national = area.area_type in ['country', 'uk']
        CoverageModel = NationalCoverage if is_national else LocalAuthorityCoverage
        
        try:
            for item in updates:
                vaccine_code = item.get('vaccine_code')
                vaccine = session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
                
                if not vaccine:
                    logger.log_action("error", "row_update", f"Vaccine not found: {vaccine_code}")
                    # Try fuzzy matching or alternative format?
                    # E.g. DTaP/IPV/Hib vs DTaP_IPV_Hib
                    if '_' in vaccine_code and '/' not in vaccine_code:
                         alt_code = vaccine_code.replace('_', '/')
                         vaccine = session.query(Vaccine).filter_by(vaccine_code=alt_code).first()
                         if vaccine:
                             logger.log_action("info", "row_update", f"Matched via replacement: {vaccine_code} -> {alt_code}")

                if not vaccine:
                     logger.log_action("error", "row_update", f"STILL Vaccine not found: {vaccine_code}")
                     continue
                    
                # Calculate percentage
                eligible = item.get('eligible_population')
                vaccinated = item.get('vaccinated_count')
                
                # Handle empty strings/nulls converting to None
                if eligible == '': eligible = None
                if vaccinated == '': vaccinated = None
                
                if eligible is not None: eligible = int(eligible)
                if vaccinated is not None: vaccinated = int(vaccinated)
                
                coverage_percentage = 0.0
                if eligible and vaccinated is not None:
                     if eligible > 0:
                        coverage_percentage = (vaccinated / eligible) * 100
                elif item.get('coverage_percentage') is not None:
                    chart_val = item.get('coverage_percentage')
                    if chart_val != '':
                        coverage_percentage = float(chart_val)

                # Find existing record
                existing = session.query(CoverageModel).filter_by(
                    area_code=area_code,
                    vaccine_id=vaccine.vaccine_id,
                    cohort_id=cohort.cohort_id,
                    year_id=year_obj.year_id
                ).first()
                
                if existing:
                    # Update existing record
                    existing.eligible_population = eligible
                    existing.vaccinated_count = vaccinated
                    existing.coverage_percentage = coverage_percentage
                else:
                    # Create new record only if we have data to save
                    if eligible is not None or vaccinated is not None:
                        new_record = CoverageModel(
                            area_code=area_code,
                            vaccine_id=vaccine.vaccine_id,
                            cohort_id=cohort.cohort_id,
                            year_id=year_obj.year_id,
                            eligible_population=eligible,
                            vaccinated_count=vaccinated,
                            coverage_percentage=coverage_percentage
                        )
                        session.add(new_record)
                success_count += 1
            
            # Commit all changes at once
            session.commit()
            # Clear session cache to ensure fresh data on next query
            session.expire_all()
            return jsonify({'message': f'Updated {success_count} records'})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'DELETE':
        data = request.json
        area_code = data.get('area_code')
        year_val = data.get('year', 2024)
        cohort_name = data.get('cohort_name', '24 months')
        
        # Delete ALL coverage for this area/cohort/year
        # We need to find them first
        year_obj = session.query(FinancialYear).filter_by(year_start=year_val).first()
        cohort = session.query(AgeCohort).filter_by(cohort_name=cohort_name).first()
        
        if not all([year_obj, cohort, area_code]):
            return jsonify({'error': 'Invalid data'}), 400
        
        # Determine which table to use based on area type
        area = session.query(GeographicArea).filter_by(area_code=area_code).first()
        if not area:
            return jsonify({'error': 'Area not found'}), 404
        
        is_national = area.area_type in ['country', 'uk']
        CoverageModel = NationalCoverage if is_national else LocalAuthorityCoverage
            
        records = session.query(CoverageModel).filter_by(
            area_code=area_code,
            cohort_id=cohort.cohort_id,
            year_id=year_obj.year_id
        ).all()
        
        count = len(records)
        for rec in records:
            session.delete(rec)
        session.commit()
        
        # Clear session cache to ensure fresh data on next query
        session.expire_all()
        return jsonify({'message': f'Deleted {count} records'})
@app.route('/api/tables/table1', methods=['POST'])
def get_table1():
    """Get Table 1: UK by country, 12 months cohort."""
    data = request.json
    cohort_name = data.get('cohort_name', '12 months')
    year = data.get('year', 2024)

    logger.log_action("query", "table1_uk_by_country", f"cohort={cohort_name}, year={year}")

    try:
        result = table_builder.get_table1_uk_by_country(cohort_name=cohort_name, year=year)
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


@app.route('/api/areas', methods=['GET'])
def get_all_areas():
    """Get all geographic areas for CRUD dropdown."""
    areas = session.query(GeographicArea).order_by(GeographicArea.area_name).all()
    return jsonify([
        {
            'code': a.area_code,
            'name': a.area_name,
            'type': a.area_type
        } for a in areas
    ])


if __name__ == '__main__':
    # Create necessary directories
    Path("static/charts").mkdir(parents=True, exist_ok=True)
    Path("static/exports").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)

    app.run(debug=True, port=5000)
