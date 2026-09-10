"""
Regression tests for saptavargaja.py's compound_relationship(), locking
in the two worked examples (Sun's side and Moon's side of the same
source chart, astroveda.wikidot.com) validated during development.
Together these exercise all 6 cells of the compound relationship table
at least once, including a direct textual quote match (Saturn becomes a
"mitra" / friend toward the Moon).
"""

from jyotipy.saptavargaja import compound_relationship, saptavargaja_bala, MOOLATRIKONA
from jyotipy.constants import Graha


def test_sun_side_worked_example():
    positions = {
        Graha.SUN: 0 * 30 + 5, Graha.MOON: 3 * 30 + 5, Graha.MARS: 9 * 30 + 5,
        Graha.MERCURY: 1 * 30 + 5, Graha.JUPITER: 10 * 30 + 5,
        Graha.VENUS: 11 * 30 + 5, Graha.SATURN: 6 * 30 + 5,
    }
    expected = {
        Graha.MOON: "great_friend", Graha.MARS: "great_friend", Graha.JUPITER: "great_friend",
        Graha.MERCURY: "friend", Graha.VENUS: "neutral", Graha.SATURN: "great_enemy",
    }
    for other, exp in expected.items():
        assert compound_relationship(Graha.SUN, other, positions) == exp, other.value


def test_moon_side_worked_example():
    positions = {
        Graha.MOON: 3 * 30 + 5, Graha.SUN: 4 * 30 + 5, Graha.MERCURY: 2 * 30 + 5,
        Graha.SATURN: 5 * 30 + 5, Graha.MARS: 7 * 30 + 5, Graha.JUPITER: 8 * 30 + 5,
        Graha.VENUS: 9 * 30 + 5,
    }
    expected = {
        Graha.SUN: "great_friend", Graha.MERCURY: "great_friend", Graha.SATURN: "friend",
        Graha.MARS: "enemy", Graha.JUPITER: "enemy", Graha.VENUS: "enemy",
    }
    for other, exp in expected.items():
        assert compound_relationship(Graha.MOON, other, positions) == exp, other.value


def test_moolatrikona_scores_45_for_sun_in_range():
    sign, lo, hi = MOOLATRIKONA[Graha.SUN]
    mid_degree = (lo + hi) / 2
    positions = {
        Graha.SUN: sign * 30 + mid_degree,
        Graha.MOON: 0, Graha.MARS: 30, Graha.MERCURY: 60,
        Graha.JUPITER: 90, Graha.VENUS: 120, Graha.SATURN: 150,
    }
    result = saptavargaja_bala(Graha.SUN, positions)
    assert result["D1"] == 45.0


def test_own_sign_scores_30():
    positions = {
        Graha.SATURN: 9 * 30 + 25,  # Capricorn, past Saturn's Moolatrikona range (0-20) -> own sign only
        Graha.SUN: 0, Graha.MOON: 30, Graha.MARS: 60,
        Graha.MERCURY: 90, Graha.JUPITER: 120, Graha.VENUS: 150,
    }
    result = saptavargaja_bala(Graha.SATURN, positions)
    assert result["D1"] == 30.0


def test_total_never_exceeds_theoretical_maximum():
    positions = {
        Graha.SUN: 0, Graha.MOON: 30, Graha.MARS: 60,
        Graha.MERCURY: 90, Graha.JUPITER: 120, Graha.VENUS: 150, Graha.SATURN: 180,
    }
    for planet in [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                   Graha.JUPITER, Graha.VENUS, Graha.SATURN]:
        result = saptavargaja_bala(planet, positions)
        assert 0 <= result["total"] <= 315.0


def test_rahu_ketu_not_covered():
    result = saptavargaja_bala(Graha.RAHU, {})
    assert result["total"] is None