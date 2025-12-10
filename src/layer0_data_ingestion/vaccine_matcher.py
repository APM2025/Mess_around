"""
Vaccine Matching and Reference Data

Unified module containing:
1. Canonical vaccine reference data
2. VaccineMatcher class for fuzzy matching
3. Convenience function for header matching

Handles inconsistent vaccine naming across CSV sources.
"""

from typing import Optional, Dict, List
from difflib import SequenceMatcher


# Canonical vaccine reference data
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


class VaccineMatcher:
    """
    Vaccine name matching with caching and fuzzy matching support.
    
    Handles inconsistent vaccine naming across CSV sources by matching
    against canonical vaccine codes and aliases.
    """
    
    def __init__(self, canonical_vaccines: list):
        """
        Initialize matcher with canonical vaccine list.
        
        Args:
            canonical_vaccines: List of vaccine dictionaries with codes, names, and aliases
        """
        self.canonical_vaccines = canonical_vaccines
        self._exact_match_index = {}
        self._alias_index = {}
        self._cache = {}
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build fast lookup indexes for exact and alias matches."""
        for vaccine in self.canonical_vaccines:
            # Index by vaccine name
            self._exact_match_index[vaccine['vaccine_name']] = vaccine['vaccine_code']
            
            # Index by all aliases
            for alias in vaccine['aliases']:
                self._alias_index[alias] = vaccine['vaccine_code']
    
    def match(self, header_text: str) -> Optional[str]:
        """
        Match CSV header to vaccine code.
        
        Args:
            header_text: Raw column header from CSV
        
        Returns:
            vaccine_code if matched, None otherwise
        """
        # Check cache first
        if header_text in self._cache:
            return self._cache[header_text]
        
        # Clean the header
        cleaned = self._clean_header(header_text)
        
        # Try exact match
        if cleaned in self._exact_match_index:
            result = self._exact_match_index[cleaned]
            self._cache[header_text] = result
            return result
        
        # Try alias match
        if cleaned in self._alias_index:
            result = self._alias_index[cleaned]
            self._cache[header_text] = result
            return result
        
        # Try fuzzy match
        result = self._fuzzy_match(cleaned)
        self._cache[header_text] = result
        return result
    
    def _clean_header(self, header: str) -> str:
        """Remove common prefixes and suffixes from header text."""
        cleaned = header.strip()
        
        # Remove common prefixes
        prefixes = [
            'Coverage at 12 months ',
            'Coverage at 24 months ',
            'Coverage at 5 years ',
            'Coverage of ',
            'Number aged 12 months ',
            'Number aged 24 months ',
            'Number aged 5 years '
        ]
        
        for prefix in prefixes:
            cleaned = cleaned.replace(prefix, '')
        
        # Remove suffixes
        cleaned = cleaned.replace(' Prim', '')
        cleaned = cleaned.replace(' (%)', '')
        cleaned = cleaned.replace('(%)', '')
        
        # Handle rotavirus vs rota
        if 'rotavirus' in cleaned.lower():
            cleaned = 'Rotavirus'
        
        return cleaned.strip()
    
    def _fuzzy_match(self, text: str) -> Optional[str]:
        """
        Fuzzy matching for partial matches.
        
        Args:
            text: Cleaned header text
        
        Returns:
            Best match vaccine_code if confidence is high enough, otherwise None
        """
        best_match = None
        best_ratio = 0.0
        threshold = 0.8  # 80% similarity required
        
        for vaccine_name, vaccine_code in self._exact_match_index.items():
            ratio = SequenceMatcher(None, text.lower(), vaccine_name.lower()).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = vaccine_code
        
        return best_match
    
    def get_match_statistics(self) -> dict:
        """Return matching statistics for debugging."""
        return {
            'cache_size': len(self._cache),
            'cache_hits': sum(1 for v in self._cache.values() if v is not None),
            'cache_misses': sum(1 for v in self._cache.values() if v is None)
        }
    
    def clear_cache(self) -> None:
        """Clear the matching cache."""
        self._cache.clear()


# Create global matcher instance for convenience
_matcher = VaccineMatcher(CANONICAL_VACCINES)


def match_vaccine_from_header(header_text: str) -> Optional[str]:
    """
    Match CSV header to canonical vaccine code.
    
    Convenience function that uses the global matcher instance.
    
    Args:
        header_text: Column header from CSV file
    
    Returns:
        vaccine_code if matched, otherwise None
    """
    return _matcher.match(header_text)
