"""
Tests for Varsha/Masa/Dina/Hora Bala. The solar-ingress root-finder is
validated against a real-world, independently-checkable anchor (Mesha
Sankranti reliably falls around April 13-14 every year); the weekday/
lordship system is validated against the plain, independently-checkable
fact that June 15 1990 was a Friday. Full coverage that "exactly one
planet" gets each of the four scores at any given moment is also
checked, since a bug that let two planets both score, or none, would be
a serious correctness problem.
"""

from datetime import datetime
from jyotipy.kalabala import (
    find_most_recent_solar_ingress, varsha_masa_dina_hora_bala, hora_lord,
    dina_bala, WEEKDAY_LORDS, CHALDEAN_ORDER,
)
from jyotipy.ayanamsa import AyanamsaSystem
from jyotipy.constants import Graha

LAT, LON = 23.0225, 72.5714


def test_mesha_sankranti_lands_mid_april():
    result = find_most_recent_solar_ingress(
        before_dt=datetime(2026, 6, 15, 12, 0, 0), utc_offset_hours=5.5,
        target_sidereal_degree=0.0, ayanamsa=AyanamsaSystem.LAHIRI,
    )
    assert result.month == 4
    assert 12 <= result.day <= 15


def test_mesha_sankranti_consistent_across_years():
    """Same well-known real-world fact, checked across 3 different years,
    not just one -- catches a root-finder that only happens to work near
    a single date."""
    for year in [2020, 2023, 2026]:
        result = find_most_recent_solar_ingress(
            before_dt=datetime(year, 6, 1, 12, 0, 0), utc_offset_hours=5.5,
            target_sidereal_degree=0.0, ayanamsa=AyanamsaSystem.LAHIRI,
        )
        assert result.year == year
        assert result.month == 4
        assert 12 <= result.day <= 15


def test_dina_bala_matches_known_weekday():
    """June 15 1990 was a Friday (independently verifiable) -> Venus
    should be the only planet scoring Dina Bala."""
    dt = datetime(1990, 6, 15, 14, 32, 0)
    scores = {p: dina_bala(p, dt, 5.5, LAT, LON)
              for p in [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                        Graha.JUPITER, Graha.VENUS, Graha.SATURN]}
    assert scores[Graha.VENUS] == 45.0
    assert sum(v for k, v in scores.items() if k != Graha.VENUS) == 0.0


def test_exactly_one_planet_scores_each_category():
    dt = datetime(1990, 6, 15, 14, 32, 0)
    planets = [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
               Graha.JUPITER, Graha.VENUS, Graha.SATURN]
    results = {p: varsha_masa_dina_hora_bala(p, dt, 5.5, LAT, LON, AyanamsaSystem.LAHIRI)
               for p in planets}

    for category in ["varsha_bala", "masa_bala", "dina_bala", "hora_bala"]:
        nonzero_count = sum(1 for r in results.values() if r[category] > 0)
        assert nonzero_count == 1, f"{category}: expected exactly 1 nonzero, got {nonzero_count}"


def test_hora_lord_changes_within_a_day():
    """Different times of the same day should generally give different
    hora lords (each hora is roughly half an hour to an hour long at
    most latitudes -- 8 hours apart should essentially always differ)."""
    lord_morning = hora_lord(datetime(1990, 6, 15, 6, 30, 0), 5.5, LAT, LON)
    lord_afternoon = hora_lord(datetime(1990, 6, 15, 14, 30, 0), 5.5, LAT, LON)
    assert lord_morning != lord_afternoon


def test_hora_lord_is_always_a_valid_classical_graha():
    dt = datetime(1990, 6, 15, 3, 17, 0)
    lord = hora_lord(dt, 5.5, LAT, LON)
    assert lord in CHALDEAN_ORDER


def test_weekday_lords_cover_all_seven_classical_grahas():
    assert set(WEEKDAY_LORDS.values()) == {
        Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
        Graha.JUPITER, Graha.VENUS, Graha.SATURN,
    }


def test_chaldean_order_is_the_seven_classical_grahas():
    assert set(CHALDEAN_ORDER) == set(WEEKDAY_LORDS.values())
    assert len(CHALDEAN_ORDER) == 7