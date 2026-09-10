"""
Regression tests for transit.py, validated against B.V. Raman's own
worked Gochara+Vedha example (Hindu Predictive Astrology, Chapter 34) --
a schematic example given in terms of houses-from-Moon directly, so
these tests check the rule logic against his stated verdicts rather than
real ephemeris longitudes.
"""

from jyotipy.transit import is_good_house, check_vedha, house_from_moon, sade_sati_status
from jyotipy.constants import Graha

MOON_SIGN = 0  # arbitrary reference; only relative houses matter here


def _sign_for_house(house: int) -> int:
    """Helper: what sign index gives this house-from-Moon, for MOON_SIGN=0."""
    return (house - 1 + MOON_SIGN) % 12


def test_raman_worked_example_sun_good_unobstructed():
    others = {Graha.MARS: _sign_for_house(8)}
    assert is_good_house(Graha.SUN, 11) is True
    assert check_vedha(Graha.SUN, 11, others, MOON_SIGN) is False


def test_raman_worked_example_moon_blocked_by_mars():
    others = {Graha.MARS: _sign_for_house(8)}
    assert is_good_house(Graha.MOON, 11) is True
    assert check_vedha(Graha.MOON, 11, others, MOON_SIGN) is True


def test_raman_worked_example_mercury_blocked_by_saturn():
    others = {Graha.SATURN: _sign_for_house(12)}
    assert is_good_house(Graha.MERCURY, 11) is True
    assert check_vedha(Graha.MERCURY, 11, others, MOON_SIGN) is True


def test_raman_worked_example_venus_blocked_by_mars():
    others = {Graha.MARS: _sign_for_house(8)}
    assert is_good_house(Graha.VENUS, 1) is True
    assert check_vedha(Graha.VENUS, 1, others, MOON_SIGN) is True


def test_raman_worked_example_jupiter_good_unobstructed():
    others = {Graha.MARS: _sign_for_house(8)}  # unrelated to Jupiter's vedha point (10)
    assert is_good_house(Graha.JUPITER, 9) is True
    assert check_vedha(Graha.JUPITER, 9, others, MOON_SIGN) is False


def test_sun_saturn_never_obstruct_each_other():
    """Documented exception: even if Saturn sits exactly on the Sun's
    vedha point, it must not trigger."""
    sun_vedha_house_for_11 = 5
    others = {Graha.SATURN: _sign_for_house(sun_vedha_house_for_11)}
    assert check_vedha(Graha.SUN, 11, others, MOON_SIGN) is False


def test_moon_mercury_never_obstruct_each_other():
    moon_vedha_house_for_11 = 8
    others = {Graha.MERCURY: _sign_for_house(moon_vedha_house_for_11)}
    assert check_vedha(Graha.MOON, 11, others, MOON_SIGN) is False


def test_rahu_ketu_alias_saturn_and_mars_tables():
    from jyotipy.transit import GOOD_HOUSES_FROM_MOON
    assert GOOD_HOUSES_FROM_MOON[Graha.RAHU] == GOOD_HOUSES_FROM_MOON[Graha.SATURN]
    assert GOOD_HOUSES_FROM_MOON[Graha.KETU] == GOOD_HOUSES_FROM_MOON[Graha.MARS]


def test_sade_sati_detects_all_three_phases():
    assert sade_sati_status(_sign_for_house(12) * 30, MOON_SIGN * 30)["phase"] == "rising (1st phase)"
    assert sade_sati_status(_sign_for_house(1) * 30, MOON_SIGN * 30)["phase"] == "peak (2nd phase)"
    assert sade_sati_status(_sign_for_house(2) * 30, MOON_SIGN * 30)["phase"] == "setting (3rd phase)"
    assert sade_sati_status(_sign_for_house(5) * 30, MOON_SIGN * 30)["sade_sati"] is False


def test_kantaka_sani_and_ashtama_sani():
    assert sade_sati_status(_sign_for_house(4) * 30, MOON_SIGN * 30)["kantaka_sani"] is True
    assert sade_sati_status(_sign_for_house(8) * 30, MOON_SIGN * 30)["ashtama_sani"] is True