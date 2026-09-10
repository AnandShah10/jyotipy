"""
Tests for dashabhukti.py. The core dominance rule is checked directly
against Raman's own quoted example (Sun Dasa / Moon Bhukti, Sun more
powerful -> Sun's significations dominate).
"""

from datetime import datetime
from jyotipy.dashabhukti import (
    meets_minimum_shadbala, dasha_bhukti_dominance, current_dasha_bhukti_lords,
    MINIMUM_SHADBALA_VIRUPAS,
)
from jyotipy.constants import Graha


def test_raman_worked_example_stronger_lord_dominates():
    """Direct Raman quote: Sun Dasa, Moon Bhukti, Sun more powerful ->
    results predominantly reflect the Sun."""
    result = dasha_bhukti_dominance(
        dasha_lord=Graha.SUN, dasha_shadbala=450.0,
        bhukti_lord=Graha.MOON, bhukti_shadbala=350.0,
    )
    assert result["dominant_lord"] == Graha.SUN


def test_dominance_flips_when_bhukti_stronger():
    result = dasha_bhukti_dominance(
        dasha_lord=Graha.SATURN, dasha_shadbala=280.0,
        bhukti_lord=Graha.JUPITER, bhukti_shadbala=500.0,
    )
    assert result["dominant_lord"] == Graha.JUPITER


def test_tie_gives_no_dominant_lord():
    result = dasha_bhukti_dominance(
        dasha_lord=Graha.VENUS, dasha_shadbala=400.0,
        bhukti_lord=Graha.MARS, bhukti_shadbala=400.0,
    )
    assert result["dominant_lord"] is None


def test_minimum_thresholds_match_sourced_table():
    assert MINIMUM_SHADBALA_VIRUPAS[Graha.SUN] == 390
    assert MINIMUM_SHADBALA_VIRUPAS[Graha.MERCURY] == 420  # highest threshold
    assert MINIMUM_SHADBALA_VIRUPAS[Graha.MARS] == 300      # 3-source majority value, not the outlier's 390
    assert MINIMUM_SHADBALA_VIRUPAS[Graha.SATURN] == 300    # tied lowest


def test_meets_minimum_true_and_false_cases():
    assert meets_minimum_shadbala(Graha.SUN, 400.0) is True
    assert meets_minimum_shadbala(Graha.SUN, 380.0) is False
    assert meets_minimum_shadbala(Graha.SUN, 390.0) is True  # exactly at threshold counts


def test_meets_minimum_none_for_rahu_ketu():
    assert meets_minimum_shadbala(Graha.RAHU, 500.0) is None
    assert meets_minimum_shadbala(Graha.KETU, 500.0) is None


def test_dominance_flags_both_meets_minimum_independently():
    """A dominant lord can still itself be below its own minimum --
    these are separate facts, both should be reported."""
    result = dasha_bhukti_dominance(
        dasha_lord=Graha.MERCURY, dasha_shadbala=350.0,  # below Mercury's 420 minimum
        bhukti_lord=Graha.SATURN, bhukti_shadbala=200.0,  # below Saturn's 300 minimum
    )
    assert result["dominant_lord"] == Graha.MERCURY  # still higher of the two
    assert result["dasha_meets_minimum"] is False    # but itself still weak
    assert result["bhukti_meets_minimum"] is False


def test_current_dasha_bhukti_lords_finds_active_period():
    mahadashas = [
        {"lord": Graha.VENUS, "start": datetime(2000, 1, 1), "end": datetime(2020, 1, 1), "years": 20},
        {"lord": Graha.SUN, "start": datetime(2020, 1, 1), "end": datetime(2026, 1, 1), "years": 6},
    ]

    def fake_antardashas(md):
        return [
            {"lord": Graha.MOON, "start": md["start"], "end": md["start"].replace(year=md["start"].year + 2)},
            {"lord": Graha.MARS, "start": md["start"].replace(year=md["start"].year + 2), "end": md["end"]},
        ]

    result = current_dasha_bhukti_lords(mahadashas, fake_antardashas, datetime(2023, 6, 1))
    assert result["mahadasha"]["lord"] == Graha.SUN
    assert result["antardasha"]["lord"] == Graha.MARS


def test_current_dasha_bhukti_lords_none_when_outside_range():
    mahadashas = [
        {"lord": Graha.VENUS, "start": datetime(2000, 1, 1), "end": datetime(2020, 1, 1), "years": 20},
    ]
    result = current_dasha_bhukti_lords(mahadashas, lambda md: [], datetime(2030, 1, 1))
    assert result["mahadasha"] is None