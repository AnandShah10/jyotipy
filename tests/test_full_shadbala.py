"""
Integration test for full_shadbala_for_chart(): checks that Yuddha Bala
actually gets detected and applied end to end when two Tara Graha are
placed in a real planetary war, and that it's correctly absent when none
are close enough to fight.
"""

from datetime import datetime
from jyotipy.shadbala import full_shadbala_for_chart
from jyotipy.constants import Graha
from jyotipy.ayanamsa import AyanamsaSystem
from jyotipy import ephemeris as eph


def _build_inputs(mars_lon, mercury_lon):
    """Build a full, internally-consistent set of chart inputs with Mars
    and Mercury placed at controlled longitudes (everyone else spread
    out normally) to force or avoid a planetary war."""
    positions = {
        Graha.SUN: 10.0, Graha.MOON: 40.0, Graha.MARS: mars_lon,
        Graha.MERCURY: mercury_lon, Graha.JUPITER: 200.0,
        Graha.VENUS: 250.0, Graha.SATURN: 300.0,
    }
    navamsha_signs = {g: 0 for g in positions}
    houses = {g: 1 for g in positions}
    birth_dt = datetime(2026, 6, 15, 14, 32, 0)
    epoch = eph.epoch_from_datetime(birth_dt, 5.5)
    return dict(
        natal_positions=positions, tropical_positions=positions,
        ascendant=10.0, midheaven=280.0, birth_dt=birth_dt,
        utc_offset_hours=5.5, latitude=23.03, longitude=72.58,
        ayanamsa=AyanamsaSystem.LAHIRI, birth_epoch=epoch,
        navamsha_signs=navamsha_signs, houses_from_ascendant=houses,
    )


def test_war_detected_and_yuddha_applied():
    inputs = _build_inputs(mars_lon=100.0, mercury_lon=100.4)  # within 1 degree
    reports = full_shadbala_for_chart(**inputs)

    mars_adj = reports[Graha.MARS]["kala_bala"].get("yuddha_bala_adjustment")
    mercury_adj = reports[Graha.MERCURY]["kala_bala"].get("yuddha_bala_adjustment")

    assert mars_adj is not None
    assert mercury_adj is not None
    assert mars_adj == -mercury_adj  # one gains exactly what the other loses
    assert not any("yuddha_bala" in m for m in reports[Graha.MARS]["missing_components"])
    assert not any("yuddha_bala" in m for m in reports[Graha.MERCURY]["missing_components"])


def test_no_war_no_adjustment():
    inputs = _build_inputs(mars_lon=100.0, mercury_lon=150.0)  # far apart
    reports = full_shadbala_for_chart(**inputs)

    assert "yuddha_bala_adjustment" not in reports[Graha.MARS]["kala_bala"]
    assert "yuddha_bala_adjustment" not in reports[Graha.MERCURY]["kala_bala"]
    assert any("yuddha_bala" in m for m in reports[Graha.MARS]["missing_components"])


def test_all_seven_planets_present_in_full_report():
    inputs = _build_inputs(mars_lon=100.0, mercury_lon=150.0)
    reports = full_shadbala_for_chart(**inputs)
    for planet in [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                   Graha.JUPITER, Graha.VENUS, Graha.SATURN]:
        assert planet in reports
        assert reports[planet]["drik_bala"] is not None