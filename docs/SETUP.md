# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd "your-project-directory"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- Flask 3.0+
- SQLAlchemy 2.0+
- pandas 2.0+
- matplotlib 3.7+
- pytest 7.4+ (for testing)
- odfpy (for ODS file support)

### 3. Initialize the Database

```bash
python create_database.py
```

This will:
- Create `data/vaccination_coverage.db`
- Load reference data (vaccines, areas, cohorts, years)
- Load coverage data from CSV files (if present in `data/csv_data/`)

Expected output:
```
======================================================================
DATABASE CREATION AND POPULATION
======================================================================

[1/5] Creating database schema...
    [OK] Database created at: data/vaccination_coverage.db

[2/5] Loading reference data...
    - Loading geographic areas...
    - Loading vaccines...
    - Loading age cohorts...
    - Loading financial years...
    [OK] Reference data loaded

[3/5] Loading coverage data...
    (If CSV files are present, they will be loaded)

[4/5] Verifying data...
    [OK] X records loaded

[5/5] Database ready!
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Troubleshooting

### "Module not found" errors

```bash
# Ensure you're in the project root directory
cd "C:\Users\amyna\OneDrive - University of Warwick\Programming for AI-MSI\New folder\Mess_around"

# Reinstall dependencies
pip install -r requirements.txt
```

### "Database file not found"

```bash
# Recreate the database
python create_database.py
```

### Port already in use

Edit `app.py` and change the port:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed from 5000
```

### Permission errors on Windows

Run your terminal as Administrator, or adjust file permissions for the `data/` directory.

## Directory Structure After Setup

```
project_root/
├── data/
│   ├── vaccination_coverage.db    # Created by create_database.py
│   └── csv_data/                   # Your CSV source files (if any)
├── logs/
│   └── web_activity.log           # Created when app runs
├── static/
│   ├── charts/                     # Generated charts
│   └── exports/                    # Exported CSV files
└── ...
```

## Next Steps

1. **Run Tests**: `pytest` to verify everything works
2. **Read Documentation**: See `docs/` folder
3. **Start Using**: Visit `http://localhost:5000`

## Development Mode

For development with auto-reload:

```bash
# The app already runs in debug mode by default
python app.py
```

Changes to Python files will automatically reload the server.

## Production Deployment

For production, use a proper WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Or use Flask's production mode:

```python
# In app.py, change:
app.run(debug=False, host='0.0.0.0', port=5000)
```

**Security Note**: Change the `SECRET_KEY` in `app.py` before deploying to production!
