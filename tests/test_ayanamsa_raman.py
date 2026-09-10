"""
Tests for ayanamsa.py, including the Raman ayanamsa's new independently-
sourced base epoch (397 CE) and rate (50 1/3 arcsec/year), replacing an
earlier version that was just a calibrated offset from Lahiri.
"""

from pymeeus.Epoch import Epoch
from jyotipy.ayanamsa import ayanamsa_raman, ayanamsa_lahiri, ayanamsa_kp_newcomb, JDE_397_CE


def test_raman_matches_rva_forum_worked_example():
    """2023 CE -> approximately 22 deg 44' 02", per the RVA forum's own
    fully worked example using this exact method."""
    e = Epoch(2023, 1, 1, 0.0)
    result = ayanamsa_raman(e)
    expected = 22 + 44 / 60 + 2 / 3600
    assert abs(result - expected) < 0.001  # within a few arcseconds


def test_raman_is_zero_at_397_ce():
    e = Epoch(397, 1, 1, 0.0)
    assert abs(ayanamsa_raman(e)) < 0.01


def test_raman_lahiri_difference_matches_independently_cited_figure():
    """Independently cited fact: Raman runs 'about 1.5 deg less than
    Lahiri' in the modern era."""
    e = Epoch(2000, 1, 1, 0.0)
    diff = ayanamsa_lahiri(e) - ayanamsa_raman(e)
    assert 1.0 < diff < 2.0


def test_raman_increases_monotonically_with_time():
    e1 = Epoch(1950, 1, 1, 0.0)
    e2 = Epoch(2000, 1, 1, 0.0)
    e3 = Epoch(2050, 1, 1, 0.0)
    assert ayanamsa_raman(e1) < ayanamsa_raman(e2) < ayanamsa_raman(e3)


def test_raman_2026_reasonable_value():
    """Sanity check: should be roughly 22.4-22.5 deg for the present day,
    consistent with the ~1.5-2 deg gap from Lahiri's ~24.2 deg."""
    e = Epoch(2026, 1, 1, 0.0)
    result = ayanamsa_raman(e)
    assert 22.0 < result < 23.0