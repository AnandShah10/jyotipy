"""
Tests for sripati_cusps(), transcribed directly from the real Swiss
Ephemeris C source (swehouse.c, case 'S'). Validated via: (1) direct
algebraic substitution matching the source's own formulas exactly, (2)
antipodal symmetry across 4 diverse ascendant/MC combinations, (3) a
signed-short-arc consistency check across the same 4 cases.

HONEST NOTE ON THE AC-SWAP BEHAVIOR: the source includes a correction
("if acmc<0, swap the Ascendant for its opposite") that its own comment
describes as being for polar-circle edge cases, but the condition
itself (acmc<0) turned out to trigger for an entirely ordinary
mid-latitude chart during testing, not just extreme latitudes. This is
transcribed faithfully (matching the real source's literal behavior)
rather than second-guessed, since deviating from the actual reference
implementation's behavior would defeat the purpose of sourcing this
directly from code. The practical effect: for some charts, Sripati's
House 1 cusp will not sit exactly at the traditional Ascendant degree.
This is flagged here explicitly rather than silently shipped.
"""

from jyotipy.houses import sripati_cusps
from jyotipy.utils import norm360


def _short_signed_arc(a, b):
    d = norm360(b - a)
    return d - 360 if d > 180 else d


TEST_CASES = [
    (19.68, 109.83),                                    # ordinary mid-latitude chart -- hits the ac-swap condition
    (190.88156009524067, 119.03788312047234),           # real Swiss Ephemeris example (Porphyry-fallback, but numbering is universal)
    (300.0, 45.0),
    (45.0, 300.0),
]


def test_matches_real_source_formula_directly():
    """Direct substitution into the source's own algebraic formulas
    (pre-swap case) must match exactly."""
    asc, mc = 190.88156009524067, 119.03788312047234  # this case doesn't trigger the swap
    acmc = norm360(asc - mc)
    if acmc > 180:
        acmc -= 360
    q1 = 180 - acmc
    s1, s4 = q1 / 3.0, acmc / 3.0
    expected_h2 = norm360(asc + s1 * 0.5)
    expected_h11 = norm360(mc + s4 * 0.5)

    cusps = sripati_cusps(asc, mc)
    assert abs(norm360(cusps[1] - expected_h2)) < 1e-6
    assert abs(norm360(cusps[10] - expected_h11)) < 1e-6


def test_antipodal_pairs_exact_across_diverse_cases():
    for asc, mc in TEST_CASES:
        cusps = sripati_cusps(asc, mc)
        for i in range(6):
            diff = abs(norm360(cusps[i] - cusps[i + 6]))
            diff = min(diff, 360 - diff)
            assert abs(diff - 180) < 1e-6, f"asc={asc},mc={mc}: pair {i+1}/{i+7} not antipodal"


def test_signed_short_arcs_consistent_across_diverse_cases():
    for asc, mc in TEST_CASES:
        cusps = sripati_cusps(asc, mc)
        arcs = [_short_signed_arc(cusps[i], cusps[(i + 1) % 12]) for i in range(12)]
        same_sign = all(a <= 1e-9 for a in arcs) or all(a >= -1e-9 for a in arcs)
        assert same_sign, f"asc={asc},mc={mc}: inconsistent rotation direction"
        assert abs(abs(sum(arcs)) - 360.0) < 1e-6


def test_ac_swap_triggers_for_the_ordinary_chart_case():
    """Documents the honest quirk: this ordinary, non-polar chart DOES
    hit the acmc<0 swap condition, meaning House 1 here is not simply
    the true Ascendant longitude."""
    asc, mc = 19.68, 109.83
    cusps = sripati_cusps(asc, mc)
    assert abs(norm360(cusps[0] - asc)) > 1.0  # confirms house1 != true ascendant here