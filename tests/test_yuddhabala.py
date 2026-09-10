"""Tests for yuddhabala.py."""

from jyotipy.yuddhabala import (
    is_planetary_war, determine_victor, yuddha_bala_magnitude,
    yuddha_bala_adjustment, find_all_wars, DISC_DIAMETER_ARCSEC,
)
from jyotipy.constants import Graha


def test_war_detected_within_one_degree():
    assert is_planetary_war(Graha.MARS, 100.0, Graha.MERCURY, 100.5) is True


def test_no_war_beyond_one_degree():
    assert is_planetary_war(Graha.MARS, 100.0, Graha.MERCURY, 102.0) is False


def test_sun_and_moon_never_participate():
    assert is_planetary_war(Graha.SUN, 100.0, Graha.MERCURY, 100.3) is False
    assert is_planetary_war(Graha.MOON, 100.0, Graha.VENUS, 100.3) is False


def test_rahu_ketu_never_participate():
    assert is_planetary_war(Graha.RAHU, 100.0, Graha.MARS, 100.3) is False


def test_war_wraps_around_360():
    assert is_planetary_war(Graha.MARS, 359.7, Graha.SATURN, 0.2) is True


def test_victor_is_more_northern_declination():
    # 90 deg tropical longitude = max northern declination (0 Cancer)
    # 30 deg tropical longitude = moderate northern declination
    winner = determine_victor(Graha.MARS, 90.0, Graha.SATURN, 30.0)
    assert winner == Graha.MARS


def test_yuddha_magnitude_uses_disc_diameter_difference():
    # Mars=9.4, Mercury=6.6 -> diff=2.8
    magnitude = yuddha_bala_magnitude(Graha.MARS, 300.0, Graha.MERCURY, 250.0)
    assert abs(magnitude - (50.0 / 2.8)) < 0.001


def test_yuddha_adjustment_full_resolution():
    result = yuddha_bala_adjustment(
        Graha.MARS, tropical_lon_a=90.0, tribala_a=300.0,
        planet_b=Graha.SATURN, tropical_lon_b=30.0, tribala_b=250.0,
    )
    assert result["winner"] == Graha.MARS
    assert result["loser"] == Graha.SATURN
    assert result["adjustment"] > 0


def test_find_all_wars_detects_pair():
    positions = {
        Graha.MARS: 100.0, Graha.MERCURY: 100.4, Graha.JUPITER: 200.0,
        Graha.VENUS: 50.0, Graha.SATURN: 300.0,
    }
    wars = find_all_wars(positions)
    assert (Graha.MARS, Graha.MERCURY) in wars or (Graha.MERCURY, Graha.MARS) in wars
    assert len(wars) == 1


def test_find_all_wars_empty_when_none_close():
    positions = {
        Graha.MARS: 100.0, Graha.MERCURY: 150.0, Graha.JUPITER: 200.0,
        Graha.VENUS: 50.0, Graha.SATURN: 300.0,
    }
    assert find_all_wars(positions) == []


def test_all_five_tara_graha_have_disc_diameters():
    for p in [Graha.MARS, Graha.MERCURY, Graha.JUPITER, Graha.VENUS, Graha.SATURN]:
        assert p in DISC_DIAMETER_ARCSEC
        assert DISC_DIAMETER_ARCSEC[p] > 0