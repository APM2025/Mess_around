"""
Tests for vaccine_matcher module.
"""

import pytest
from src.layer0_data_ingestion.vaccine_matcher import (
    VaccineMatcher,
    CANONICAL_VACCINES,
    match_vaccine_from_header
)


@pytest.fixture
def matcher():
    """Create vaccine matcher instance."""
    return VaccineMatcher(CANONICAL_VACCINES)


# Phase 1: Basic instantiation
def test_vaccine_matcher_can_be_created():
    """Test that VaccineMatcher can be instantiated."""
    matcher = VaccineMatcher(CANONICAL_VACCINES)

    assert matcher is not None
    assert len(matcher.canonical_vaccines) > 0


def test_vaccine_matcher_builds_indexes():
    """Test that VaccineMatcher builds internal indexes."""
    matcher = VaccineMatcher(CANONICAL_VACCINES)

    assert len(matcher._exact_match_index) > 0
    assert len(matcher._alias_index) > 0


# Phase 2: Exact matching tests
def test_match_exact_vaccine_name(matcher):
    """Test exact match by vaccine name."""
    result = matcher.match('MMR1')

    assert result == 'MMR1'


def test_match_dtap_exact(matcher):
    """Test exact match for DTaP/IPV/Hib/HepB."""
    result = matcher.match('DTaP/IPV/Hib/HepB')

    assert result == 'DTaP_IPV_Hib_HepB'


def test_match_rotavirus(matcher):
    """Test exact match for Rotavirus."""
    result = matcher.match('Rotavirus')

    assert result == 'Rota'


# Phase 3: Alias matching tests
def test_match_alias_mmr_space(matcher):
    """Test alias matching for 'MMR 1' with space."""
    result = matcher.match('MMR 1')

    assert result == 'MMR1'


def test_match_alias_dtap_prim(matcher):
    """Test alias matching for 'DTaP/IPV/Hib/HepB Prim'."""
    result = matcher.match('DTaP/IPV/Hib/HepB Prim')

    assert result == 'DTaP_IPV_Hib_HepB'


def test_match_alias_pcv(matcher):
    """Test alias matching for 'PCV'."""
    result = matcher.match('PCV')

    assert result == 'PCV1'


# Phase 4: Header cleaning tests
def test_match_with_coverage_prefix(matcher):
    """Test matching with 'Coverage at 12 months' prefix."""
    result = matcher.match('Coverage at 12 months MMR1')

    assert result == 'MMR1'


def test_match_with_coverage_prefix_24_months(matcher):
    """Test matching with 'Coverage at 24 months' prefix."""
    result = matcher.match('Coverage at 24 months DTaP/IPV/Hib/HepB')

    assert result == 'DTaP_IPV_Hib_HepB'


def test_match_with_percentage_suffix(matcher):
    """Test matching with percentage suffix."""
    result = matcher.match('MMR1 (%)')

    assert result == 'MMR1'


def test_match_with_number_aged_prefix(matcher):
    """Test matching with 'Number aged' prefix."""
    result = matcher.match('Number aged 12 months MMR1')

    assert result == 'MMR1'


# Phase 5: Fuzzy matching tests
def test_fuzzy_match_slight_typo(matcher):
    """Test fuzzy matching with slight variation."""
    # "MMR1" vs "MMR 1" should match via alias, but let's test fuzzy logic
    result = matcher.match('MMR dose 1')

    assert result == 'MMR1'


def test_fuzzy_match_menb_booster(matcher):
    """Test fuzzy matching for MenB booster."""
    result = matcher.match('MenB boos')

    assert result == 'MenB_booster'


def test_fuzzy_match_no_match_below_threshold(matcher):
    """Test fuzzy matching returns None for poor matches."""
    result = matcher.match('Completely Invalid Vaccine Name')

    assert result is None


# Phase 6: Case sensitivity tests
def test_match_case_insensitive_mmr(matcher):
    """Test case-insensitive matching."""
    result = matcher.match('mmr1')

    # Should still match despite lowercase
    # This depends on implementation - adjust if needed
    assert result is not None


def test_match_case_insensitive_rotavirus(matcher):
    """Test case-insensitive matching for rotavirus."""
    result = matcher.match('rotavirus')

    assert result == 'Rota'


# Phase 7: Caching tests
def test_cache_is_used(matcher):
    """Test that caching improves performance."""
    # First call
    result1 = matcher.match('MMR1')

    # Check cache was populated
    assert 'MMR1' in matcher._cache

    # Second call should use cache
    result2 = matcher.match('MMR1')

    assert result1 == result2
    assert result2 == 'MMR1'


def test_clear_cache(matcher):
    """Test cache can be cleared."""
    # Populate cache
    matcher.match('MMR1')
    assert len(matcher._cache) > 0

    # Clear cache
    matcher.clear_cache()
    assert len(matcher._cache) == 0


def test_get_match_statistics(matcher):
    """Test match statistics reporting."""
    # Make some matches
    matcher.match('MMR1')
    matcher.match('Invalid Vaccine')

    stats = matcher.get_match_statistics()

    assert 'cache_size' in stats
    assert 'cache_hits' in stats
    assert 'cache_misses' in stats
    assert stats['cache_size'] == 2
    assert stats['cache_hits'] == 1  # MMR1 matched
    assert stats['cache_misses'] == 1  # Invalid didn't match


# Phase 8: Convenience function tests
def test_match_vaccine_from_header_function():
    """Test the convenience function works."""
    result = match_vaccine_from_header('Coverage at 12 months MMR1')

    assert result == 'MMR1'


def test_match_vaccine_from_header_with_dtap():
    """Test convenience function with complex vaccine."""
    result = match_vaccine_from_header('Coverage at 24 months DTaP/IPV/Hib/HepB')

    assert result == 'DTaP_IPV_Hib_HepB'


def test_match_vaccine_from_header_no_match():
    """Test convenience function with no match."""
    result = match_vaccine_from_header('Invalid Vaccine Header')

    assert result is None


# Phase 9: All canonical vaccines are matchable
def test_all_canonical_vaccines_matchable(matcher):
    """Test that all canonical vaccines can be matched by their name."""
    for vaccine in CANONICAL_VACCINES:
        result = matcher.match(vaccine['vaccine_name'])

        assert result == vaccine['vaccine_code'], \
            f"Failed to match {vaccine['vaccine_name']}"


def test_all_canonical_vaccines_have_required_fields():
    """Test that all canonical vaccines have required fields."""
    for vaccine in CANONICAL_VACCINES:
        assert 'vaccine_code' in vaccine
        assert 'vaccine_name' in vaccine
        assert 'description' in vaccine
        assert 'aliases' in vaccine
        assert isinstance(vaccine['aliases'], list)


# Phase 10: Edge cases
def test_match_empty_string(matcher):
    """Test matching empty string."""
    result = matcher.match('')

    assert result is None


def test_match_whitespace_only(matcher):
    """Test matching whitespace-only string."""
    result = matcher.match('   ')

    assert result is None


def test_match_with_extra_whitespace(matcher):
    """Test matching with extra whitespace."""
    result = matcher.match('  MMR1  ')

    assert result == 'MMR1'


# Phase 11: Specific vaccine tests
def test_match_pcv_booster(matcher):
    """Test matching PCV booster."""
    result = matcher.match('PCV booster')

    assert result == 'PCV_booster'


def test_match_hib_menc_booster(matcher):
    """Test matching Hib/MenC booster."""
    result = matcher.match('Hib/MenC booster')

    assert result == 'Hib_MenC_booster'


def test_match_dtap_ipv_booster(matcher):
    """Test matching dTaP/IPV booster."""
    result = matcher.match('dTaP/IPV booster')

    assert result == 'dTaP_IPV_booster'


def test_match_dtap_ipv_booster_uppercase(matcher):
    """Test matching DTaP/IPV booster with uppercase."""
    result = matcher.match('DTaP/IPV booster')

    assert result == 'dTaP_IPV_booster'


def test_match_hepb(matcher):
    """Test matching Hepatitis B."""
    result = matcher.match('Hepatitis B')

    assert result == 'HepB'


def test_match_hepb_short(matcher):
    """Test matching HepB short form."""
    result = matcher.match('HepB')

    assert result == 'HepB'


def test_match_bcg(matcher):
    """Test matching BCG."""
    result = matcher.match('BCG')

    assert result == 'BCG'


def test_match_menb(matcher):
    """Test matching MenB."""
    result = matcher.match('MenB')

    assert result == 'MenB'


def test_match_menb_booster(matcher):
    """Test matching MenB booster."""
    result = matcher.match('MenB Booster')

    assert result == 'MenB_booster'
