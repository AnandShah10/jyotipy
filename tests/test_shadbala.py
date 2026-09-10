"""
Regression tests for shadbala.py. Uchcha Bala is validated against two
independent worked numeric examples from two different sources. The
other implemented sub-components (Ojayugmarasyamsa, Kendradi, Drekkana,
Dig, Naisargika) are tested for correct formula behavior and boundary
conditions rather than against full worked examples, since none of the
sources provided complete numeric worked examples for those specific
sub-components in isolation.
"""

from jyotipy.shadbala import (
    uchcha_bala, ojayugmarasyamsa_bala, kendradi_bala, drekkana_bala,
    dig_bala, naisargika_bala, sthana_bala, shadbala_report,
    NAISARGIKA_BALA,
)
from jyotipy.constants import Graha


def test_uchcha_bala_worked_example_saravali():
    sun_lon = 2 * 30 + 12  # 12 deg Gemini
    assert abs(uchcha_bala(Graha.SUN, sun_lon) - 39.33) < 0.01


def test_uchcha_bala_worked_example_roxyapi():
    sun_lon = (10 + 40) % 360
    assert abs(uchcha_bala(Graha.SUN, sun_lon) - 46.67) < 0.01


def test_uchcha_bala_full_strength_at_exact_exaltation():
    assert abs(uchcha_bala(Graha.SUN, 10.0) - 60.0) < 0.001


def test_uchcha_bala_zero_at_exact_debilitation():
    assert abs(uchcha_bala(Graha.SUN, 190.0) - 0.0) < 0.001


def test_naisargika_bala_fixed_ranking():
    order = [Graha.SUN, Graha.MOON, Graha.VENUS, Graha.JUPITER,
             Graha.MERCURY, Graha.MARS, Graha.SATURN]
    values = [naisargika_bala(p) for p in order]
    assert values == sorted(values, reverse=True)
    assert naisargika_bala(Graha.SUN) == 60.0
    assert naisargika_bala(Graha.SATURN) == 8.57


def test_ojayugmarasyamsa_male_planet_odd_sign():
    # Sun (male) in Aries (sign 0, odd) rashi and Gemini (sign 2, odd) navamsha
    assert ojayugmarasyamsa_bala(Graha.SUN, 5.0, 2) == 30.0


def test_ojayugmarasyamsa_female_planet_even_sign():
    # Moon (female) in Taurus (sign 1, even) rashi and Cancer (sign 3, even) navamsha
    assert ojayugmarasyamsa_bala(Graha.MOON, 1 * 30 + 5, 3) == 30.0


def test_ojayugmarasyamsa_zero_when_wrong_parity():
    # Sun (wants odd) in Taurus (even sign) -> 0 for that half
    assert ojayugmarasyamsa_bala(Graha.SUN, 1 * 30 + 5, 2) == 15.0  # only navamsha (odd) scores


def test_kendradi_bala_three_tiers():
    assert kendradi_bala(1) == 60.0
    assert kendradi_bala(4) == 60.0
    assert kendradi_bala(2) == 30.0
    assert kendradi_bala(11) == 30.0
    assert kendradi_bala(3) == 15.0
    assert kendradi_bala(12) == 15.0


def test_drekkana_bala_by_planet_gender_and_decanate():
    assert drekkana_bala(Graha.SUN, 5.0) == 15.0     # male, 1st decanate
    assert drekkana_bala(Graha.SUN, 15.0) == 0.0      # male, 2nd decanate -> no score
    assert drekkana_bala(Graha.MOON, 15.0) == 15.0    # female, 2nd decanate
    assert drekkana_bala(Graha.MERCURY, 25.0) == 15.0  # neutral, 3rd decanate


def test_dig_bala_full_strength_at_own_angle():
    ascendant = 45.0
    midheaven = 315.0  # roughly square, doesn't need to be exact for this test
    # Jupiter's strongest house is 1 (ascendant) -> full 60 at ascendant degree
    assert abs(dig_bala(Graha.JUPITER, ascendant, ascendant, midheaven) - 60.0) < 0.01


def test_dig_bala_zero_at_opposite_angle():
    ascendant = 45.0
    midheaven = 315.0
    opposite_of_ascendant = (ascendant + 180) % 360
    assert abs(dig_bala(Graha.JUPITER, opposite_of_ascendant, ascendant, midheaven) - 0.0) < 0.01


def test_sthana_bala_now_includes_saptavargaja():
    natal_positions = {
        Graha.SUN: 10.0, Graha.MOON: 40.0, Graha.MARS: 70.0,
        Graha.MERCURY: 100.0, Graha.JUPITER: 130.0, Graha.VENUS: 160.0, Graha.SATURN: 190.0,
    }
    result = sthana_bala(Graha.SUN, 10.0, navamsha_sign=0, house_from_ascendant=1,
                          natal_positions=natal_positions)
    assert result["saptavargaja_bala"] is not None
    assert result["saptavargaja_bala"] > 0
    assert "total" in result


def test_shadbala_report_flags_only_remaining_missing_components():
    from datetime import datetime
    natal_positions = {
        Graha.SUN: 10.0, Graha.MOON: 40.0, Graha.MARS: 70.0,
        Graha.MERCURY: 100.0, Graha.JUPITER: 130.0, Graha.VENUS: 160.0, Graha.SATURN: 190.0,
    }
    from jyotipy.ayanamsa import AyanamsaSystem
    report = shadbala_report(
        Graha.SUN, sidereal_longitude=10.0, navamsha_sign=0,
        house_from_ascendant=1, ascendant=10.0, midheaven=280.0,
        natal_positions=natal_positions, tropical_positions=natal_positions,
        birth_dt=datetime(2026, 6, 15, 14, 32, 0), utc_offset_hours=5.5,
        latitude=23.03, longitude=72.58, ayanamsa=AyanamsaSystem.LAHIRI,
    )
    assert report["kala_bala"] is not None
    assert report["chesta_bala"] is not None  # Sun has a Chesta Bala substitute
    assert report["drik_bala"] is not None    # Drik Bala is now implemented
    assert "chesta_bala" not in report["missing_components"]  # Sun's IS implemented
    # Yuddha Bala can't resolve from a single planet in isolation -- still flagged here.
    assert any("yuddha_bala" in m for m in report["missing_components"])
    assert report["sthana_bala"]["saptavargaja_bala"] is not None


def test_shadbala_report_chesta_bala_missing_without_epoch_for_non_luminaries():
    """Without birth_epoch supplied, Chesta Bala for non-luminaries
    correctly falls back to None rather than guessing."""
    from datetime import datetime
    natal_positions = {
        Graha.SUN: 10.0, Graha.MOON: 40.0, Graha.MARS: 70.0,
        Graha.MERCURY: 100.0, Graha.JUPITER: 130.0, Graha.VENUS: 160.0, Graha.SATURN: 190.0,
    }
    from jyotipy.ayanamsa import AyanamsaSystem
    report = shadbala_report(
        Graha.MARS, sidereal_longitude=70.0, navamsha_sign=3,
        house_from_ascendant=5, ascendant=10.0, midheaven=280.0,
        natal_positions=natal_positions, tropical_positions=natal_positions,
        birth_dt=datetime(2026, 6, 15, 14, 32, 0), utc_offset_hours=5.5,
        latitude=23.03, longitude=72.58, ayanamsa=AyanamsaSystem.LAHIRI,
    )
    assert report["chesta_bala"] is None
    assert "chesta_bala" in report["missing_components"]


def test_shadbala_report_chesta_bala_computed_for_non_luminaries_with_epoch():
    """With birth_epoch supplied (as chart.py always does), Chesta Bala
    for non-luminaries IS computed -- this is the real, wired-up path."""
    from datetime import datetime
    from jyotipy import ephemeris as eph
    natal_positions = {
        Graha.SUN: 10.0, Graha.MOON: 40.0, Graha.MARS: 70.0,
        Graha.MERCURY: 100.0, Graha.JUPITER: 130.0, Graha.VENUS: 160.0, Graha.SATURN: 190.0,
    }
    from jyotipy.ayanamsa import AyanamsaSystem
    birth_dt = datetime(2026, 6, 15, 14, 32, 0)
    epoch = eph.epoch_from_datetime(birth_dt, 5.5)
    report = shadbala_report(
        Graha.MARS, sidereal_longitude=70.0, navamsha_sign=3,
        house_from_ascendant=5, ascendant=10.0, midheaven=280.0,
        natal_positions=natal_positions, tropical_positions=natal_positions,
        birth_dt=birth_dt, utc_offset_hours=5.5,
        latitude=23.03, longitude=72.58, ayanamsa=AyanamsaSystem.LAHIRI,
        birth_epoch=epoch,
    )
    assert report["chesta_bala"] is not None
    assert 0.0 <= report["chesta_bala"] <= 60.0
    assert "chesta_bala" not in report["missing_components"]