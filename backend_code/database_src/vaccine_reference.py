"""
Canonical Vaccine Reference Data

Defines the official list of vaccines tracked in the database with standardized names
and aliases to handle inconsistent naming across different CSV source files.

Structure:
- vaccine_code: Database identifier
- vaccine_name: Official standardized name
- description: What the vaccine protects against
- aliases: Alternative names found in CSV files
"""

CANONICAL_VACCINES = [
    {
        'vaccine_code': 'DTaP_IPV_Hib_HepB',
        'vaccine_name': 'DTaP/IPV/Hib/HepB',
        'description': 'Diphtheria, Tetanus, Pertussis, Polio, Hib, Hepatitis B (6-in-1)',
        'aliases': ['DTaP/IPV/Hib/HepB Prim', 'DTaP IPV Hib HepB']
    },
    {
        'vaccine_code': 'DTaP_IPV_Hib',
        'vaccine_name': 'DTaP/IPV/Hib',
        'description': 'Diphtheria, Tetanus, Pertussis, Polio, Hib (5-in-1)',
        'aliases': ['DTaP/IPV/Hib Prim']
    },
    {
        'vaccine_code': 'MMR1',
        'vaccine_name': 'MMR1',
        'description': 'Measles, Mumps, Rubella (First Dose)',
        'aliases': ['MMR 1', 'MMR dose 1']
    },
    {
        'vaccine_code': 'MMR2',
        'vaccine_name': 'MMR2',
        'description': 'Measles, Mumps, Rubella (Second Dose)',
        'aliases': ['MMR 2', 'MMR dose 2']
    },
    {
        'vaccine_code': 'PCV1',
        'vaccine_name': 'PCV1',
        'description': 'Pneumococcal Conjugate Vaccine (First Dose)',
        'aliases': ['PCV 1', 'PCV dose 1', 'PCV']
    },
    {
        'vaccine_code': 'PCV_booster',
        'vaccine_name': 'PCV Booster',
        'description': 'Pneumococcal Conjugate Vaccine (Booster)',
        'aliases': ['PCV booster', 'PCV boos']
    },
    {
        'vaccine_code': 'Rota',
        'vaccine_name': 'Rotavirus',
        'description': 'Rotavirus vaccine',
        'aliases': ['rota', 'Rota']
    },
    {
        'vaccine_code': 'MenB',
        'vaccine_name': 'MenB',
        'description': 'Meningococcal B vaccine',
        'aliases': []
    },
    {
        'vaccine_code': 'MenB_booster',
        'vaccine_name': 'MenB Booster',
        'description': 'Meningococcal B vaccine (Booster)',
        'aliases': ['MenB booster', 'MenB boos']
    },
    {
        'vaccine_code': 'Hib_MenC_booster',
        'vaccine_name': 'Hib/MenC Booster',
        'description': 'Hib and Meningococcal C booster',
        'aliases': ['Hib/MenC booster', 'Hib MenC booster']
    },
    {
        'vaccine_code': 'dTaP_IPV_booster',
        'vaccine_name': 'dTaP/IPV Booster',
        'description': 'Pre-school booster',
        'aliases': ['dTaP/IPV booster', 'DTaP/IPV booster']
    },
    {
        'vaccine_code': 'HepB',
        'vaccine_name': 'Hepatitis B',
        'description': 'Hepatitis B vaccine for eligible children',
        'aliases': ['HepB', 'Hep B']
    },
    {
        'vaccine_code': 'BCG',
        'vaccine_name': 'BCG',
        'description': 'BCG (Bacillus Calmette-Guérin) vaccine for eligible children',
        'aliases': []
    },
]



# Create global matcher instance for backward compatibility
from backend_code.database_src.vaccine_matcher import VaccineMatcher
_matcher = VaccineMatcher(CANONICAL_VACCINES)


def match_vaccine_from_header(header_text: str) -> str:
    """
    Match CSV header to canonical vaccine code.
    
    Args:
        header_text: Column header from CSV file
    
    Returns:
        vaccine_code if matched, otherwise None
    """
    return _matcher.match(header_text)
