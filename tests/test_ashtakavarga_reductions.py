"""
Tests for trikona_sodhana() and ekadhipatya_sodhana(). No external numeric
worked example was available for these two reduction techniques (unlike
the base Ashtakavarga bindu tables, which ARE validated against B.V.
Raman's published example) -- so these tests instead exhaustively cover
every rule branch exactly as stated in the source, to make sure each one
is actually implemented, not just the common case.
"""

from jyotipy.ashtakavarga import trikona_sodhana, ekadhipatya_sodhana, reduced_bhinnashtakavarga
from jyotipy.constants import Graha


def _bav_with_trine(a, b, c, fill=0):
    """12-element BAV with the Aries/Leo/Sagittarius trine set to a,b,c
    and everything else set to `fill` (chosen high enough that it never
    accidentally interacts with the other 3 trine groups in these tests)."""
    bav = [fill] * 12
    bav[0], bav[4], bav[8] = a, b, c
    return bav


def test_trikona_unequal_no_zero_subtracts_minimum():
    bav = _bav_with_trine(5, 3, 7, fill=9)
    result = trikona_sodhana(bav)
    assert (result[0], result[4], result[8]) == (2, 0, 4)


def test_trikona_one_zero_present_no_reduction():
    bav = _bav_with_trine(0, 3, 7, fill=9)
    result = trikona_sodhana(bav)
    assert (result[0], result[4], result[8]) == (0, 3, 7)


def test_trikona_two_zeros_forces_third_to_zero():
    """The one genuinely non-obvious rule: naive min-subtraction would
    leave the third sign at 5, but the classical rule forces it to 0."""
    bav = _bav_with_trine(0, 0, 5, fill=9)
    result = trikona_sodhana(bav)
    assert (result[0], result[4], result[8]) == (0, 0, 0)


def test_trikona_all_equal_nonzero_eliminates_all():
    bav = _bav_with_trine(4, 4, 4, fill=9)
    result = trikona_sodhana(bav)
    assert (result[0], result[4], result[8]) == (0, 0, 0)


def test_trikona_all_zero_stays_zero():
    bav = _bav_with_trine(0, 0, 0, fill=9)
    result = trikona_sodhana(bav)
    assert (result[0], result[4], result[8]) == (0, 0, 0)


def test_trikona_only_touches_its_own_group():
    bav = [5, 3, 7, 2, 4, 6, 1, 8, 5, 3, 2, 1]  # arbitrary, no special structure
    result = trikona_sodhana(bav)
    # Water group: Cancer(3)=2, Scorpio(7)=8, Pisces(11)=1 -- unequal, no zero -> subtract min(1)
    assert (result[3], result[7], result[11]) == (1, 7, 0)


def test_ekadhipatya_both_occupied_no_reduction():
    bav = [0] * 12
    bav[0], bav[7] = 5, 2  # Aries/Scorpio, Mars's pair
    occupied = [False] * 12
    occupied[0] = occupied[7] = True
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (5, 2)


def test_ekadhipatya_zero_present_no_reduction():
    bav = [0] * 12
    bav[0], bav[7] = 0, 6
    occupied = [False] * 12
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (0, 6)


def test_ekadhipatya_one_occupied_higher_eliminates_unoccupied():
    bav = [0] * 12
    bav[0], bav[7] = 6, 3  # Aries occupied with more bindus than unoccupied Scorpio
    occupied = [False] * 12
    occupied[0] = True
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (6, 0)


def test_ekadhipatya_one_occupied_lower_pulls_unoccupied_down_to_match():
    bav = [0] * 12
    bav[0], bav[7] = 3, 6  # Aries occupied with FEWER bindus than unoccupied Scorpio
    occupied = [False] * 12
    occupied[0] = True
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (3, 3)


def test_ekadhipatya_one_occupied_equal_eliminates_unoccupied():
    bav = [0] * 12
    bav[0], bav[7] = 4, 4
    occupied = [False] * 12
    occupied[0] = True
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (4, 0)


def test_ekadhipatya_both_unoccupied_equal_eliminates_both():
    bav = [0] * 12
    bav[0], bav[7] = 5, 5
    occupied = [False] * 12
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (0, 0)


def test_ekadhipatya_both_unoccupied_unequal_converts_larger_to_smaller():
    bav = [0] * 12
    bav[0], bav[7] = 6, 2
    occupied = [False] * 12
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[0], result[7]) == (2, 2)


def test_ekadhipatya_sun_moon_signs_never_touched():
    """Leo (Sun) and Cancer (Moon) own one sign each and must never be
    reduced by this pass, regardless of values."""
    bav = [0] * 12
    bav[4], bav[3] = 7, 1  # Leo, Cancer -- deliberately very unequal
    occupied = [False] * 12
    result = ekadhipatya_sodhana(bav, occupied)
    assert (result[4], result[3]) == (7, 1)


def test_reduced_bav_never_exceeds_unreduced():
    """Sanity check independent of any specific rule: reduction should
    never INCREASE a bindu count anywhere (matches steer.coach's
    independent claim: 'it never raises a score')."""
    from jyotipy.ashtakavarga import bhinnashtakavarga
    positions = {
        Graha.SUN: 10.0, Graha.MOON: 40.0, Graha.MARS: 70.0,
        Graha.MERCURY: 100.0, Graha.JUPITER: 130.0, Graha.VENUS: 160.0, Graha.SATURN: 190.0,
    }
    ascendant = 20.0
    unreduced = bhinnashtakavarga(Graha.SUN, positions, ascendant)
    reduced = reduced_bhinnashtakavarga(Graha.SUN, positions, ascendant)
    assert all(r <= u for r, u in zip(reduced, unreduced))