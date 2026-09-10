"""
Regression tests for chesta_bala_non_luminary(), validated against the
well-documented, independently verifiable 2020 Mars retrograde period
(stationed retrograde Sep 9 2020, opposition/mid-retrograde ~Oct 13,
stationed direct Nov 13 2020 -- all publicly documented astronomical
facts, not classical-text claims). Chesta Bala should rise toward the
retrograde window, peak near opposition, and fall away afterward --
this is checked directly rather than against a single BPHS numeric
worked example, since none was found specifically for this component.
"""

from datetime import datetime
from jyotipy import ephemeris as eph
from jyotipy.kalabala import chesta_bala_non_luminary
from jyotipy.constants import Graha


def _mars_chesta(dt):
    epoch = eph.epoch_from_datetime(dt, 0.0)
    trop = eph.tropical_longitudes(epoch)
    return chesta_bala_non_luminary(Graha.MARS, epoch, trop[Graha.MARS])


def test_chesta_bala_in_valid_range():
    for dt in [datetime(2020, 1, 1), datetime(2020, 6, 1), datetime(2020, 10, 13), datetime(2021, 3, 1)]:
        val = _mars_chesta(dt)
        assert 0.0 <= val <= 60.0


def test_chesta_bala_peaks_near_documented_opposition():
    """Value at the documented mid-retrograde/opposition date should be
    close to the theoretical maximum of 60."""
    peak_value = _mars_chesta(datetime(2020, 10, 13))
    assert peak_value > 55.0


def test_chesta_bala_rises_approaching_retrograde_window():
    far_before = _mars_chesta(datetime(2020, 6, 1))
    approaching = _mars_chesta(datetime(2020, 8, 15))
    at_station = _mars_chesta(datetime(2020, 9, 9))
    near_opposition = _mars_chesta(datetime(2020, 10, 13))
    assert far_before < approaching < at_station < near_opposition


def test_chesta_bala_falls_after_stationing_direct():
    at_station_direct = _mars_chesta(datetime(2020, 11, 13))
    well_after = _mars_chesta(datetime(2021, 1, 15))
    near_opposition = _mars_chesta(datetime(2020, 10, 13))
    assert near_opposition > at_station_direct > well_after


def test_chesta_bala_low_near_solar_conjunction():
    """April 2020 is well before the retrograde window, closer to
    conjunction with the Sun -- should score noticeably lower than the
    opposition peak."""
    near_conjunction = _mars_chesta(datetime(2020, 4, 1))
    near_opposition = _mars_chesta(datetime(2020, 10, 13))
    assert near_conjunction < near_opposition - 20


def test_all_five_non_luminary_planets_computable():
    dt = datetime(2020, 10, 13)
    epoch = eph.epoch_from_datetime(dt, 0.0)
    trop = eph.tropical_longitudes(epoch)
    for planet in [Graha.MERCURY, Graha.VENUS, Graha.MARS, Graha.JUPITER, Graha.SATURN]:
        val = chesta_bala_non_luminary(planet, epoch, trop[planet])
        assert 0.0 <= val <= 60.0