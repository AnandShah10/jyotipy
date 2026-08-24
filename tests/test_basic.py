"""
Smoke tests. These check internal consistency (angles in range, dasha
sums to 120 years, etc.) rather than asserting exact arcsecond agreement
with a reference ephemeris, since we don't have network access to a
reference source in this dev environment. Anand: cross-check a real
birth chart against JHora/Swiss Ephemeris output before trusting this
for anything real -- see README "Validation" section.
"""

from datetime import datetime
from jyotipy import BirthChart, Graha, SIGNS
from jyotipy.constants import VIMSHOTTARI_YEARS


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
    # Lahiri ayanamsa in 1990 should be roughly 23.6-23.7 deg
    assert 23.0 < chart.ayanamsa_value < 24.5


def test_whole_sign_houses_are_sign_boundaries():
    chart = make_chart()
    cusps = chart.houses("whole_sign")
    assert len(cusps) == 12
    for c in cusps:
        assert c % 30 == 0, f"whole sign cusp {c} not on a sign boundary"


def test_rahu_ketu_are_opposite():
    chart = make_chart()
    rahu = chart.positions[Graha.RAHU]
    ketu = chart.positions[Graha.KETU]
    diff = abs((rahu - ketu) % 360)
    assert abs(diff - 180) < 0.001


def test_navamsha_sign_index_in_range():
    chart = make_chart()
    d9 = chart.varga("D9")
    for g, sign_idx in d9.items():
        assert 0 <= sign_idx <= 11


def test_mahadasha_full_cycle_sums_to_120_years():
    chart = make_chart()
    periods = chart.mahadashas(cycles=1)
    total = sum(p["years"] for p in periods)
    # The loop runs until total >= 120y, so the last period can overshoot
    # slightly past the 120y mark (dasha periods don't divide evenly
    # against an arbitrary birth moment) -- that's correct, not a bug.
    assert 120.0 <= total < 120.0 + 20.0


def test_antardasha_sums_to_mahadasha_duration():
    chart = make_chart()
    md = chart.mahadashas()[1]  # a full (non-partial) mahadasha
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


def test_summary_and_print():
    chart = make_chart()
    print("\n--- Ascendant ---")
    print(f"  {SIGNS[int(chart.ascendant // 30)]} {chart.ascendant % 30:.2f} deg")
    print(f"  Ayanamsa (Lahiri): {chart.ayanamsa_value:.4f} deg")
    print("\n--- Graha positions (sidereal) ---")
    for g, info in chart.summary().items():
        print(f"  {g:8s} {info['sign']:12s} {info['degree_in_sign']:6.2f}  "
              f"{info['name']:16s} pada {info['pada']}")
    print("\n--- Panchanga ---")
    p = chart.panchanga()
    print(f"  Tithi: {p['tithi']['paksha']} {p['tithi']['name']}")
    print(f"  Yoga: {p['yoga']['name']}")
    print(f"  Karana: {p['karana']['name']}")
    print(f"  Vara: {p['vara']}")
    print("\n--- First 3 Mahadashas ---")
    for md in chart.mahadashas()[:3]:
        print(f"  {md['lord'].value:8s} {md['start'].date()} -> {md['end'].date()}  ({md['years']:.2f}y)")
    print("\n--- Yogas ---")
    for k, v in chart.yogas().items():
        print(f"  {k}: {v}")
