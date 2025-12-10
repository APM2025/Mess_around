"""
UK Vaccination Coverage Dashboard - Source Code

4-Layer Architecture:
- Layer 0: Data Ingestion & Cleaning
- Layer 1: Database Layer (models, session management)
- Layer 2: Business Logic (analysis, CRUD, export)
- Layer 3: Presentation (visualization, web interface)

See ARCHITECTURE.md for detailed layer descriptions and dependency rules.
"""

__version__ = "3.0.0"
__author__ = "Amyna"

# Expose layer packages
__all__ = [
    "layer0_data_ingestion",
    "layer1_database",
    "layer2_business_logic",
    "layer3_presentation",
]
