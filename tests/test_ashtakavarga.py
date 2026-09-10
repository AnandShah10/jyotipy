"""
Regression tests for Ashtakavarga, validated against B.V. Raman's own
published "Standard Horoscope" worked example (Ashtakavarga System of
Prediction, Chapters 9-16) -- a real chart with hand-computed results
from the source text itself, not just an internal consistency check.
"""

from jyotipy.ashtakavarga import (
    bhinnashtakavarga, sarvashtakavarga, EXPECTED_TOTALS, EXPECTED_SAV_TOTAL,
)
from jyotipy.constants import Graha

# B.V. Raman's Standard Horoscope: born Oct 16 1918, 2:00 PM LMT, Bangalore.
RAMAN_POSITIONS = {
    Graha.SUN: 179 + 8 / 60,
    Graha.MOON: 10 * 30 + 9 + 34 / 60,     # Aquarius
    Graha.MARS: 229 + 49 / 60,
    Graha.MERCURY: 180 + 33 / 60,
    Graha.JUPITER: 83 + 35 / 60,
    Graha.VENUS: 170 + 4 / 60,
    Graha.SATURN: 124 + 51 / 60,
}
RAMAN_ASCENDANT = 294 + 57 / 60  # Capricorn

RAMAN_EXPECTED_BAV = {
    Graha.SUN:     [5, 3, 5, 4, 4, 4, 3, 5, 5, 0, 5, 5],
    Graha.MOON:    [5, 3, 5, 5, 3, 2, 3, 4, 6, 5, 3, 5],
    Graha.MARS:    [4, 3, 4, 3, 4, 1, 1, 5, 3, 2, 5, 4],
    Graha.MERCURY: [4, 6, 4, 5, 5, 5, 3, 6, 4, 4, 5, 3],
    Graha.JUPITER: [3, 4, 7, 6, 4, 4, 6, 4, 5, 5, 4, 4],
    Graha.VENUS:   [7, 4, 4, 3, 3, 4, 5, 3, 4, 5, 4, 6],
    Graha.SATURN:  [5, 2, 4, 4, 3, 3, 5, 2, 3, 3, 1, 4],
}

RAMAN_EXPECTED_SAV = [33, 25, 33, 30, 26, 23, 26, 29, 30, 24, 27, 31]


def test_each_planet_matches_raman_worked_example():
    for planet, expected in RAMAN_EXPECTED_BAV.items():
        got = bhinnashtakavarga(planet, RAMAN_POSITIONS, RAMAN_ASCENDANT)
        assert got == expected, f"{planet.value}: got {got}, expected {expected}"


def test_each_planet_total_matches_classical_checksum():
    for planet, expected_total in EXPECTED_TOTALS.items():
        bav = bhinnashtakavarga(planet, RAMAN_POSITIONS, RAMAN_ASCENDANT)
        assert sum(bav) == expected_total


def test_sarvashtakavarga_matches_raman_worked_example():
    sav = sarvashtakavarga(RAMAN_POSITIONS, RAMAN_ASCENDANT)
    assert sav == RAMAN_EXPECTED_SAV
    assert sum(sav) == EXPECTED_SAV_TOTAL == 337


def test_ashtakavarga_is_position_dependent():
    """Sanity check independent of the worked example: shifting a planet
    should change at least one sign's bindu count somewhere."""
    shifted = dict(RAMAN_POSITIONS)
    shifted[Graha.MARS] = (shifted[Graha.MARS] + 45) % 360
    bav_before = bhinnashtakavarga(Graha.SUN, RAMAN_POSITIONS, RAMAN_ASCENDANT)
    bav_after = bhinnashtakavarga(Graha.SUN, shifted, RAMAN_ASCENDANT)
    assert bav_before != bav_after
    assert sum(bav_after) == 48  # total is fixed regardless of positions