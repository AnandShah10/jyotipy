from datetime import datetime
from jyotipy import BirthChart, Graha, SIGNS
from jyotipy.constants import VARGA_DIVISIONS


def make_chart():
    return BirthChart(
        dt=datetime(1990, 6, 15, 14, 32, 0),
        utc_offset_hours=5.5,
        latitude=23.0225, longitude=72.5714,  # Ahmedabad
    )


def test_all_longitudes_in_range():
    chart = make_chart()
    for g, lon in chart.positions.items():
        assert 0 <= lon < 360, f"{g} longitude {lon} out of range"
    assert 0 <= chart.ascendant < 360
    assert 0 <= chart.midheaven < 360


def test_ayanamsa_reasonable_for_1990():
    chart = make_chart()
    assert 23.0 < chart.ayanamsa_value < 24.5


def test_whole_sign_houses_are_sign_boundaries():
    chart = make_chart()
    cusps = chart.houses("whole_sign")
    assert len(cusps) == 12
    for c in cusps:
        assert c % 30 == 0


def test_rahu_ketu_are_opposite():
    chart = make_chart()
    rahu = chart.positions[Graha.RAHU]
    ketu = chart.positions[Graha.KETU]
    diff = abs((rahu - ketu) % 360)
    assert abs(diff - 180) < 0.001


def test_all_16_vargas_run_and_in_range():
    """Every divisional chart, D1 through D60, should now run without
    raising NotImplementedError and produce a valid 0-11 sign index."""
    chart = make_chart()
    for div in VARGA_DIVISIONS:
        result = chart.varga(div)
        for g, sign_idx in result.items():
            assert 0 <= sign_idx <= 11, f"{div} gave out-of-range sign for {g}"


def test_d30_matches_sourced_worked_examples():
    """Direct regression test against the two independently-sourced
    worked examples used to validate D30 during development."""
    from jyotipy.varga import d30_trimshamsha
    assert SIGNS[d30_trimshamsha(2.0)] == "Aries"      # Aries 0-5deg -> Mars -> Aries
    assert SIGNS[d30_trimshamsha(7.0)] == "Aquarius"   # Aries 5-10deg -> Saturn -> Aquarius
    assert SIGNS[d30_trimshamsha(14.0)] == "Sagittarius"  # Aries 10-18deg -> Jupiter -> Sagittarius
    pisces_26_07 = 11 * 30 + 26 + 7 / 60
    assert SIGNS[d30_trimshamsha(pisces_26_07)] == "Scorpio"


def test_d60_matches_sourced_worked_example():
    from jyotipy.varga import d60_shashtiamsha
    leo_3_10 = 4 * 30 + 3 + 10 / 60
    assert SIGNS[d60_shashtiamsha(leo_3_10)] == "Aquarius"


def test_navamsha_sign_index_in_range():
    chart = make_chart()
    d9 = chart.varga("D9")
    for g, sign_idx in d9.items():
        assert 0 <= sign_idx <= 11


def test_mahadasha_full_cycle_sums_to_120_years():
    chart = make_chart()
    periods = chart.mahadashas(cycles=1)
    total = sum(p["years"] for p in periods)
    assert 120.0 <= total < 120.0 + 20.0


def test_antardasha_sums_to_mahadasha_duration():
    chart = make_chart()
    md = chart.mahadashas()[1]
    ads = chart.antardashas(md)
    assert len(ads) == 9
    total = sum(a["years"] for a in ads)
    assert abs(total - md["years"]) < 0.01


def test_panchanga_runs():
    chart = make_chart()
    p = chart.panchanga()
    assert p["tithi"]["number"] in range(1, 31)
    assert p["vara"] in ["Sunday", "Monday", "Tuesday", "Wednesday",
                          "Thursday", "Friday", "Saturday"]


def test_yogas_runs():
    chart = make_chart()
    y = chart.yogas()
    assert "gajakesari" in y
    assert isinstance(y["gajakesari"], bool)
