"""
Test Fixtures - Sample CSV Data for Testing

This file contains small, controlled CSV data samples for testing.
Each fixture represents a specific test scenario.
"""

# Sample data mimicking the actual COVER CSV structure
# This would normally be in separate CSV files in tests/fixtures/

SAMPLE_VACCINES_CSV = """Area,DTaP/IPV/Hib,MMR,PCV
England,91.3,93.1,95.2
Scotland,94.5,95.4,96.1
Wales,94.1,95.7,94.8
"""

SAMPLE_UTLA_CSV = """Code,UTLA Name,DTaP/IPV/Hib,MMR
E08000025,Birmingham,89.2,87.5
E08000003,Manchester,90.1,88.9
E08000035,Leeds,92.3,91.2
E06000047,County Durham,94.1,93.5
"""

# Edge case: Missing data
SAMPLE_CSV_WITH_MISSING = """Area,DTaP/IPV/Hib,MMR
England,91.3,
Scotland,,95.4
Wales,94.1,95.7
"""

# Edge case: Suppressed data ([z] notation)
SAMPLE_CSV_WITH_SUPPRESSION = """Area,DTaP/IPV/Hib,MMR
England,91.3,[z]
Scotland,94.5,95.4
"""
