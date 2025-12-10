"""
Main Entry Point for Vaccination Coverage Dashboard

Run this file to start the Flask web application:
    python main.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.layer3_presentation.flask_app import app

if __name__ == '__main__':
    # Create necessary directories
    (project_root / "static/charts").mkdir(parents=True, exist_ok=True)
    (project_root / "static/exports").mkdir(parents=True, exist_ok=True)
    (project_root / "logs").mkdir(parents=True, exist_ok=True)
    
    # Run the Flask application
    app.run(debug=True, port=5000)
