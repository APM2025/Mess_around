# Flask Web Dashboard for Vaccination Coverage System

## Overview
A comprehensive web-based dashboard that integrates all vaccination coverage modules:
- Data analysis and filtering
- Interactive visualizations
- CRUD operations
- CSV exports
- Activity logging

## Prerequisites
Make sure you have installed Flask:
```bash
pip install flask
```

## Quick Start

### 1. Ensure Database is Populated
```bash
python create_database.py
```

### 2. Run the Flask Application
```bash
python app.py
```

### 3. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

## Dashboard Features

### 📊 Summary Tab
- **Summary Statistics**: View count, mean, min, max coverage
- **Top Performing Areas**: See the top 5 areas by coverage

### 📈 Charts Tab
- **Top Areas Chart**: Horizontal bar chart of top performing areas
- **Coverage Trend**: Line chart showing historical trends
- **Summary Statistics Chart**: Bar chart of mean/min/max
- **Coverage Distribution**: Histogram showing distribution

### 📋 Data Table Tab
- View filtered vaccination data
- Export to CSV for further analysis

### 📝 Activity Logs Tab
- View recent user actions
- Track all queries, exports, and visualizations

## Using the Dashboard

### Step 1: Select Data
1. Choose a vaccine from the dropdown (e.g., MMR1, DTaP)
2. Select age cohort (24 months, 12 months, or 5 years)
3. Set number of top areas to display

### Step 2: Load Data
- Click **"Load Summary"** to see statistics
- Click **"Load Top Areas"** to see best performers
- Click **"Generate All Charts"** to create visualizations

### Step 3: Export Data
- Click **"Export to CSV"** to download filtered data
- File will be saved in `static/exports/` and opened in browser

## API Endpoints

### Data Analysis
- `GET /api/vaccines` - List all vaccines
- `POST /api/filter` - Filter vaccination data
- `POST /api/summary` - Get summary statistics
- `POST /api/top-areas` - Get top performing areas
- `POST /api/trend` - Get coverage trend over time

### Visualizations
- `POST /api/visualize/top-areas` - Generate top areas chart
- `POST /api/visualize/trend` - Generate trend chart
- `POST /api/visualize/summary` - Generate summary chart
- `POST /api/visualize/distribution` - Generate distribution chart

### Export & Logging
- `POST /api/export/csv` - Export data to CSV
- `GET /api/logs/recent` - Get recent activity logs
- `GET /api/logs/summary` - Get log summary statistics

### CRUD Operations
- `GET/POST/PUT/DELETE /api/crud/vaccines` - Manage vaccines

## Directory Structure
```
├── app.py                      # Flask application
├── templates/
│   └── dashboard.html          # Main dashboard UI
├── static/
│   ├── charts/                 # Generated visualizations
│   └── exports/                # CSV exports
├── logs/
│   └── web_activity.log       # User activity log
└── database_version_2/         # All backend modules
    ├── src/
    │   ├── fs_analysis.py     # Data analysis
    │   ├── visualization.py    # Chart generation
    │   ├── crud.py            # Database operations
    │   ├── export.py          # CSV export
    │   └── user_log.py        # Activity logging
    └── tests/                  # Test suite
```

## Example Workflow

### 1. Analyze MMR1 Coverage
```
1. Select "MMR1" from vaccine dropdown
2. Keep cohort as "24 months"
3. Click "Load Summary" → See statistics
4. Click "Load Top Areas" → See best performers
```

### 2. Generate Visualizations
```
1. Set "Top N Areas" to 10
2. Click "Generate All Charts"
3. Switch to "Charts" tab
4. View all 4 generated charts
```

### 3. Export Data
```
1. With filters applied
2. Click "Export to CSV"
3. CSV file downloads automatically
4. Contains all filtered records
```

### 4. View Activity
```
1. Switch to "Activity Logs" tab
2. See all recent actions
3. Timestamps and details included
```

## Troubleshooting

### "No data found" error
- Ensure database is populated: `python create_database.py`
- Check vaccine code is valid (e.g., 'MMR1' not 'mmr1')
- Verify cohort name matches database ('24 months' with space)

### Charts not displaying
- Check `static/charts/` directory exists
- Ensure matplotlib is installed
- Try refreshing the browser (Ctrl+F5)

### Port already in use
Change port in app.py:
```python
app.run(debug=True, port=5001)  # Use different port
```

## Features Integrated

✅ **Analysis Module**: Filter data, calculate statistics, find trends
✅ **Visualization Module**: Generate 4 types of charts
✅ **CRUD Module**: Manage vaccines and coverage records
✅ **Export Module**: Download data as CSV
✅ **Logging Module**: Track all user actions

## Notes

- All actions are automatically logged to `logs/web_activity.log`
- Charts are cached in `static/charts/` (refresh with timestamp)
- CSV exports saved to `static/exports/`
- Dashboard is responsive and works on mobile devices

## Next Steps

To extend the dashboard:
1. Add user authentication
2. Add more CRUD forms for other entities
3. Add real-time updates with WebSockets
4. Add data validation and error handling
5. Add more advanced filtering options
6. Add chart customization options

Enjoy your comprehensive vaccination coverage dashboard!
