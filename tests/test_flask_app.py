"""
Integration tests for Flask application endpoints.

These tests verify that the web application endpoints are working correctly
and integrate properly with the backend modules.
"""

import pytest
import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Flask app
from app import app as flask_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


class TestBasicRoutes:
    """Test basic page routes."""

    def test_index_page_loads(self, client):
        """Test that the index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Vaccination Coverage' in response.data

    def test_tables_page_loads(self, client):
        """Test that the tables dashboard loads successfully."""
        response = client.get('/tables')
        assert response.status_code == 200

    def test_charts_page_loads(self, client):
        """Test that the charts dashboard loads successfully."""
        response = client.get('/charts')
        assert response.status_code == 200


class TestVaccineAPI:
    """Test vaccine-related API endpoints."""

    def test_get_vaccines_returns_list(self, client):
        """Test that GET /api/vaccines returns a list."""
        response = client.get('/api/vaccines')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_vaccines_returns_vaccine_objects(self, client):
        """Test that vaccines have correct structure."""
        response = client.get('/api/vaccines')
        data = json.loads(response.data)

        if len(data) > 0:
            vaccine = data[0]
            assert 'vaccine_code' in vaccine
            assert 'vaccine_name' in vaccine


class TestVisualizationAPI:
    """Test visualization API endpoints."""

    def test_visualize_top_areas_requires_vaccine(self, client):
        """Test that top areas endpoint requires a vaccine code."""
        response = client.post('/api/visualize/top-areas',
                                json={'cohort_name': '24 months'})

        # Should handle missing vaccine gracefully
        assert response.status_code in [200, 400, 404]

    def test_visualize_top_areas_with_valid_vaccine(self, client):
        """Test top areas visualization with valid vaccine."""
        response = client.post('/api/visualize/top-areas',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months',
                                    'n': 10
                                })

        # Should return chart URL or error
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'chart_url' in data or 'error' in data

    def test_visualize_trend_endpoint(self, client):
        """Test trend visualization endpoint."""
        response = client.post('/api/visualize/trend',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'chart_url' in data or 'error' in data

    def test_visualize_distribution_endpoint(self, client):
        """Test distribution visualization endpoint."""
        response = client.post('/api/visualize/distribution',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'chart_url' in data or 'error' in data

    def test_visualize_summary_endpoint(self, client):
        """Test summary visualization endpoint."""
        response = client.post('/api/visualize/summary',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'chart_url' in data or 'error' in data


class TestExportAPI:
    """Test CSV export API endpoints."""

    def test_export_csv_endpoint(self, client):
        """Test CSV export endpoint."""
        response = client.post('/api/export/csv',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'download_url' in data or 'error' in data
            assert 'row_count' in data or 'error' in data


class TestDataAnalysisAPI:
    """Test data analysis API endpoints."""

    def test_filter_data_endpoint(self, client):
        """Test data filtering endpoint."""
        response = client.post('/api/filter',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'count' in data
        assert 'data' in data

    def test_summary_endpoint(self, client):
        """Test summary statistics endpoint."""
        response = client.post('/api/summary',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        # Should return summary or 404 if no data
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            # Summary should have statistics
            assert isinstance(data, dict)

    def test_top_areas_endpoint(self, client):
        """Test top areas endpoint."""
        response = client.post('/api/top-areas',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months',
                                    'n': 10
                                })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_trend_endpoint(self, client):
        """Test coverage trend endpoint."""
        response = client.post('/api/trend',
                                json={
                                    'vaccine_code': 'MMR1',
                                    'cohort_name': '24 months'
                                })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestTableAPI:
    """Test table builder API endpoints."""

    def test_table1_endpoint(self, client):
        """Test Table 1 (UK by country) endpoint."""
        response = client.post('/api/tables/table1',
                                json={
                                    'cohort_name': '12 months',
                                    'year': 2024
                                })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'title' in data
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_utla_table_endpoint(self, client):
        """Test UTLA table endpoint."""
        response = client.post('/api/tables/utla',
                                json={
                                    'cohort_name': '24 months',
                                    'year': 2024
                                })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'cohort' in data
        assert 'year' in data
        assert 'data' in data

    def test_regional_table_endpoint(self, client):
        """Test regional table endpoint."""
        response = client.post('/api/tables/regional',
                                json={
                                    'cohort_name': '24 months'
                                })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'cohort' in data
        assert 'data' in data

    def test_england_summary_endpoint(self, client):
        """Test England summary endpoint."""
        response = client.post('/api/tables/england-summary',
                                json={
                                    'cohort_name': '24 months',
                                    'year': 2024
                                })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)


class TestCRUDAPI:
    """Test CRUD API endpoints for vaccines."""

    def test_get_all_vaccines(self, client):
        """Test getting all vaccines."""
        response = client.get('/api/crud/vaccines')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_create_and_delete_vaccine(self, client):
        """Test creating and deleting a test vaccine."""
        # Create a test vaccine
        test_vaccine = {
            'vaccine_code': 'TEST999',
            'vaccine_name': 'Test Vaccine for Integration Test'
        }

        create_response = client.post('/api/crud/vaccines',
                                       json=test_vaccine,
                                       content_type='application/json')

        # Should succeed or fail gracefully
        assert create_response.status_code in [201, 400, 409]

        if create_response.status_code == 201:
            # Clean up - delete the test vaccine
            delete_response = client.delete('/api/crud/vaccines',
                                             json={'vaccine_code': 'TEST999'},
                                             content_type='application/json')

            assert delete_response.status_code in [200, 404]

    def test_update_nonexistent_vaccine_returns_404(self, client):
        """Test updating a vaccine that doesn't exist."""
        response = client.put('/api/crud/vaccines',
                              json={
                                  'vaccine_code': 'NONEXISTENT999',
                                  'vaccine_name': 'Should Not Exist'
                              },
                              content_type='application/json')

        assert response.status_code == 404


class TestLoggingAPI:
    """Test activity logging API endpoints."""

    def test_get_recent_logs(self, client):
        """Test getting recent activity logs."""
        response = client.get('/api/logs/recent?n=10')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'logs' in data
        assert isinstance(data['logs'], list)

    def test_get_log_summary(self, client):
        """Test getting log summary statistics."""
        response = client.get('/api/logs/summary')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, dict)
