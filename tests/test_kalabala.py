"""Regression tests for kalabala.py, locking in the BPHS-quoted checkpoints
validated during development (Ayana Bala = 30 at zero declination is a
direct textual quote, not derived)."""

from datetime import datetime
from jyotipy.kalabala import ayana_bala, nathonnata_bala, paksha_bala, tribhaga_bala
from jyotipy.constants import Graha


def test_ayana_bala_thirty_at_zero_declination():
    """Direct BPHS quote: 'The Ayana Bala at Zero Declination is 30.'"""
    assert ayana_bala(Graha.SUN, 0.0) == 30.0
    assert ayana_bala(Graha.MOON, 0.0) == 30.0
    assert ayana_bala(Graha.MERCURY, 0.0) == 30.0


def test_ayana_bala_max_and_min_at_solstice_points():
    assert abs(ayana_bala(Graha.SUN, 90.0) - 60.0) < 0.01      # Sun plus-on-north: peaks at max north
    assert abs(ayana_bala(Graha.MOON, 90.0) - 0.0) < 0.01       # Moon plus-on-south: minimum at max north
    assert abs(ayana_bala(Graha.SUN, 270.0) - 0.0) < 0.01       # Sun: minimum at max south
    assert abs(ayana_bala(Graha.MOON, 270.0) - 60.0) < 0.01     # Moon: peaks at max south


def test_mercury_ayana_always_uses_absolute_kranti():
    # Mercury should score identically at max-north and max-south (symmetric).
    north = ayana_bala(Graha.MERCURY, 90.0)
    south = ayana_bala(Graha.MERCURY, 270.0)
    assert abs(north - south) < 0.01
    assert abs(north - 60.0) < 0.01


def test_nathonnata_bala_boundary_values():
    assert nathonnata_bala(Graha.SUN, datetime(2026, 1, 1, 0, 0, 0)) == 0.0
    assert nathonnata_bala(Graha.SUN, datetime(2026, 1, 1, 12, 0, 0)) == 60.0
    assert nathonnata_bala(Graha.MOON, datetime(2026, 1, 1, 0, 0, 0)) == 60.0
    assert nathonnata_bala(Graha.MOON, datetime(2026, 1, 1, 12, 0, 0)) == 0.0


def test_nathonnata_mercury_always_full():
    for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
        assert nathonnata_bala(Graha.MERCURY, datetime(2026, 1, 1, hour, 0, 0)) == 60.0


def test_nathonnata_sun_moon_are_complements():
    dt = datetime(2026, 1, 1, 7, 30, 0)
    sun_val = nathonnata_bala(Graha.SUN, dt)
    moon_val = nathonnata_bala(Graha.MOON, dt)
    assert abs((sun_val + moon_val) - 60.0) < 0.001


def test_paksha_bala_full_moon_and_new_moon():
    assert paksha_bala(Graha.MOON, moon_tropical=180.0, sun_tropical=0.0) == 60.0
    assert paksha_bala(Graha.SUN, moon_tropical=180.0, sun_tropical=0.0) == 0.0
    assert paksha_bala(Graha.MOON, moon_tropical=0.0, sun_tropical=0.0) == 0.0
    assert paksha_bala(Graha.SUN, moon_tropical=0.0, sun_tropical=0.0) == 60.0


def test_paksha_bala_benefic_malefic_are_complements():
    val_moon = paksha_bala(Graha.MOON, moon_tropical=100.0, sun_tropical=20.0)
    val_sun = paksha_bala(Graha.SUN, moon_tropical=100.0, sun_tropical=20.0)
    assert abs((val_moon + val_sun) - 60.0) < 0.001


def test_tribhaga_jupiter_always_full():
    for is_day in (True, False):
        for third in (0, 1, 2):
            assert tribhaga_bala(Graha.JUPITER, is_day, third) == 60.0


def test_tribhaga_day_thirds_correct_rulers():
    assert tribhaga_bala(Graha.MERCURY, True, 0) == 60.0
    assert tribhaga_bala(Graha.SUN, True, 1) == 60.0
    assert tribhaga_bala(Graha.SATURN, True, 2) == 60.0
    assert tribhaga_bala(Graha.MERCURY, True, 1) == 0.0


def test_tribhaga_night_thirds_correct_rulers():
    assert tribhaga_bala(Graha.MOON, False, 0) == 60.0
    assert tribhaga_bala(Graha.VENUS, False, 1) == 60.0
    assert tribhaga_bala(Graha.MARS, False, 2) == 60.0
    assert tribhaga_bala(Graha.MOON, False, 1) == 0.0