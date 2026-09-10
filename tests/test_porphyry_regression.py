"""
Regression test for a real bug in porphyry_cusps() found while building
Sripati on top of it. The original implementation computed each
quadrant's arc independently via "(end-start) % 360", which silently
computed the wrong (long) arc whenever the raw longitude relationship
between quadrant boundaries didn't happen to favor the forward
direction -- for the specific chart below, this caused houses 1, 5, and
9 to all collapse to nearly the same degree, which is obviously wrong
for a system whose whole point is spreading houses around the full
circle. Fixed by computing quadrant 4's signed short arc once and
deriving the other 3 quadrants from the mathematical constraint that
opposite quadrants are equal (quadrant1 = quadrant3 = 180 - quadrant4;
quadrant2 = quadrant4) -- the same constraint the real Swiss Ephemeris
source encodes for its own Sripati implementation, which is what
surfaced this bug in the first place.
"""

from jyotipy.houses import porphyry_cusps
from jyotipy.utils import norm360


def _short_signed_arc(a, b):
    d = norm360(b - a)
    return d - 360 if d > 180 else d


def test_houses_1_5_9_are_not_collapsed():
    """The original bug: houses 1, 5, 9 all landed within ~0.1 deg of
    each other for this exact chart. They must be spread around the
    circle instead."""
    asc, mc = 19.68, 109.83
    cusps = porphyry_cusps(asc, mc)
    h1, h5, h9 = cusps[0], cusps[4], cusps[8]
    assert abs(norm360(h1 - h5)) > 30
    assert abs(norm360(h5 - h9)) > 30
    assert abs(norm360(h1 - h9)) > 30


def test_signed_short_arcs_consistent():
    asc, mc = 19.68, 109.83
    cusps = porphyry_cusps(asc, mc)
    arcs = [_short_signed_arc(cusps[i], cusps[(i + 1) % 12]) for i in range(12)]
    assert all(a <= 0 for a in arcs) or all(a >= 0 for a in arcs)
    assert abs(abs(sum(arcs)) - 360.0) < 1e-6


def test_antipodal_pairs_exact():
    asc, mc = 19.68, 109.83
    cusps = porphyry_cusps(asc, mc)
    for i in range(6):
        diff = abs(norm360(cusps[i] - cusps[i + 6]))
        diff = min(diff, 360 - diff)
        assert abs(diff - 180) < 1e-6


def test_consistent_across_diverse_cases():
    cases = [(19.68, 109.83), (190.88156009524067, 119.03788312047234), (300.0, 45.0), (45.0, 300.0)]
    for asc, mc in cases:
        cusps = porphyry_cusps(asc, mc)
        arcs = [_short_signed_arc(cusps[i], cusps[(i + 1) % 12]) for i in range(12)]
        assert all(a <= 1e-9 for a in arcs) or all(a >= -1e-9 for a in arcs)
        for i in range(6):
            diff = abs(norm360(cusps[i] - cusps[i + 6]))
            diff = min(diff, 360 - diff)
            assert abs(diff - 180) < 1e-6