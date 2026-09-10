"""
Tests for drikbala.py, locking in the source's own worked example
(Jupiter aspecting the Sun from 192 deg away -> +13.5) plus 4 additional
grid spot-checks used to reconstruct the formula during development.
"""

from jyotipy.drikbala import drsti_bala_magnitude, drik_bala
from jyotipy.constants import Graha


def test_worked_example_jupiter_aspects_sun():
    assert abs(drsti_bala_magnitude(192.0) - 13.5) < 0.001


def test_grid_spot_checks():
    assert abs(drsti_bala_magnitude(220.0) - 10.0) < 0.001
    assert abs(drsti_bala_magnitude(280.0) - 2.5) < 0.001
    assert abs(drsti_bala_magnitude(100.0) - 10.0) < 0.001
    assert abs(drsti_bala_magnitude(70.0) - 6.25) < 0.001


def test_max_at_opposition():
    assert abs(drsti_bala_magnitude(180.0) - 15.0) < 0.001


def test_zero_near_conjunction():
    assert drsti_bala_magnitude(15.0) == 0.0
    assert drsti_bala_magnitude(340.0) == 0.0


def test_full_drik_bala_matches_worked_example_end_to_end():
    positions = {Graha.SUN: 0.0, Graha.JUPITER: 168.0}  # (0 - 168) mod 360 = 192
    result = drik_bala(Graha.SUN, positions)
    assert result["contributions"]["Jupiter"] == 13.5
    assert result["total"] == 13.5


def test_jupiter_and_mercury_always_positive():
    """Even at an angle where the raw magnitude is nonzero, Jupiter and
    Mercury's contributions must never be negative."""
    positions = {Graha.MOON: 0.0, Graha.JUPITER: 260.0, Graha.MERCURY: 260.0}
    result = drik_bala(Graha.MOON, positions)
    assert result["contributions"]["Jupiter"] >= 0
    assert result["contributions"]["Mercury"] >= 0


def test_malefic_contribution_is_negative():
    positions = {Graha.MOON: 0.0, Graha.SATURN: 180.0}
    result = drik_bala(Graha.MOON, positions, moon_is_waxing=True)
    assert result["contributions"]["Saturn"] < 0


def test_waning_moon_is_malefic_waxing_is_benefic():
    positions = {Graha.SUN: 0.0, Graha.MOON: 180.0}
    waxing = drik_bala(Graha.SUN, positions, moon_is_waxing=True)
    waning = drik_bala(Graha.SUN, positions, moon_is_waxing=False)
    assert waxing["contributions"]["Moon"] > 0
    assert waning["contributions"]["Moon"] < 0


def test_rahu_ketu_excluded_from_contributions():
    positions = {Graha.SUN: 0.0, Graha.RAHU: 180.0, Graha.KETU: 0.0, Graha.MARS: 90.0}
    result = drik_bala(Graha.SUN, positions)
    assert "Rahu" not in result["contributions"]
    assert "Ketu" not in result["contributions"]


def test_drik_bala_can_be_negative_overall():
    """A planet surrounded mostly by malefics should show a negative
    total -- this is a real result, not something to clamp to zero."""
    positions = {Graha.MOON: 0.0, Graha.SUN: 180.0, Graha.MARS: 175.0, Graha.SATURN: 185.0}
    result = drik_bala(Graha.MOON, positions)
    assert result["total"] < 0