"""
Ascendant (Lagna), Midheaven, and house cusp systems.

The ascendant/MC formulas here are the standard spherical-astronomy
formulas (Meeus, "Astronomical Algorithms", ch. on ecliptic points),
using local sidereal time (RAMC), the obliquity of the ecliptic, and
geographic latitude. Everything is computed in the TROPICAL frame first
(because RAMC/obliquity are tropical-frame quantities by definition),
then the ascendant longitude is converted to sidereal by the caller
(chart.py) using the same ayanamsa as the grahas, so the whole chart
stays internally consistent.

House systems implemented:
  - Whole Sign (Rashi-based)
  - Equal House
  - Porphyry (quadrant trisection)
  - True Placidus (iterative semi-arc trisection) -- see the extensive
    module comment further down for the debugging history on this one.
  - Sripati -- see its own comment block; this one turned out to be
    simple once the actual Swiss Ephemeris source code (not prose
    documentation) was consulted directly: Sripati cusps are exactly
    the midpoints of adjacent Porphyry cusps.
"""

from pymeeus.Epoch import Epoch
from pymeeus import Coordinates
import math

from .utils import norm360


def ascendant_tropical(epoch: Epoch, latitude_deg: float, longitude_deg: float) -> float:
    obliquity = float(Coordinates.true_obliquity(epoch))
    nutation = float(Coordinates.nutation_longitude(epoch))
    gst_days = float(epoch.apparent_sidereal_time(obliquity, nutation))
    ramc = norm360(gst_days * 360.0 + longitude_deg)

    theta = math.radians(ramc)
    eps = math.radians(obliquity)
    phi = math.radians(latitude_deg)

    y = -math.cos(theta)
    x = math.sin(eps) * math.tan(phi) + math.cos(eps) * math.sin(theta)
    asc = math.degrees(math.atan2(y, x))
    return norm360(asc)


def midheaven_tropical(epoch: Epoch, longitude_deg: float) -> float:
    obliquity = float(Coordinates.true_obliquity(epoch))
    nutation = float(Coordinates.nutation_longitude(epoch))
    gst_days = float(epoch.apparent_sidereal_time(obliquity, nutation))
    ramc = norm360(gst_days * 360.0 + longitude_deg)

    theta = math.radians(ramc)
    eps = math.radians(obliquity)
    mc = math.degrees(math.atan2(math.sin(theta), math.cos(theta) * math.cos(eps)))
    return norm360(mc)


def whole_sign_cusps(sidereal_ascendant: float) -> list:
    asc_sign_start = (int(sidereal_ascendant // 30)) * 30
    return [norm360(asc_sign_start + 30 * i) for i in range(12)]


def equal_house_cusps(sidereal_ascendant: float) -> list:
    return [norm360(sidereal_ascendant + 30 * i) for i in range(12)]


def porphyry_cusps(sidereal_ascendant: float, sidereal_mc: float) -> list:
    """
    Porphyry cusps: each of the 4 quadrants (Asc-IC, IC-Desc, Desc-MC,
    MC-Asc) is trisected using its OWN signed short arc. This naturally
    and automatically satisfies the required antipodal constraint
    (quadrant1 = quadrant3, quadrant2 = quadrant4) without needing any
    special-case correction -- verified across 4 diverse charts, all
    four quadrant arcs come out matching that constraint exactly and
    summing to precisely +-360 deg on their own.

    BUG FIX HISTORY: an earlier version computed each quadrant's arc via
    a naive forward-only "(end-start) % 360", which broke for charts
    where the raw longitude relationship between quadrant boundaries
    didn't favor the forward direction -- for one real test chart, this
    collapsed houses 1, 5, and 9 to nearly the same degree. A second
    attempt tried to derive quadrant sizes from a single signed arc plus
    a mathematical constraint (mirroring how Sripati's own formula is
    built in the real Swiss Ephemeris source) but that required an
    additional Ascendant-swap correction to stay self-consistent, which
    felt like it was fighting the geometry rather than describing it.
    The simpler fix here -- just take each quadrant's own short arc
    directly -- turns out to already satisfy the antipodal constraint
    automatically, with no swap needed, and keeps House 1 always
    exactly at the true Ascendant (unlike Sripati, where the swap is a
    genuine, source-verified part of that specific algorithm).
    """
    asc, mc = sidereal_ascendant, sidereal_mc
    ic = norm360(mc + 180)
    desc = norm360(asc + 180)

    def signed_short_arc(start, end):
        d = norm360(end - start)
        return d - 360.0 if d > 180.0 else d

    def trisect(start, arc, n=3):
        return [norm360(start + arc * k / n) for k in range(n)]

    q1 = trisect(asc, signed_short_arc(asc, ic))      # houses 1,2,3
    q2 = trisect(ic, signed_short_arc(ic, desc))      # houses 4,5,6
    q3 = trisect(desc, signed_short_arc(desc, mc))    # houses 7,8,9
    q4 = trisect(mc, signed_short_arc(mc, asc))       # houses 10,11,12
    return q1 + q2 + q3 + q4


def sripati_cusps(sidereal_ascendant: float, sidereal_mc: float) -> list:
    """
    Sripati house cusps, transcribed DIRECTLY from the real Swiss
    Ephemeris C source (swehouse.c, case 'S') -- not routed through
    this module's own general-purpose Porphyry function, deliberately.

    An earlier attempt tried to express Sripati as "midpoint of
    adjacent Porphyry cusps" using porphyry_cusps() above, reasoning
    that the two should agree conceptually. That's true in principle,
    but reconciling it in practice meant making porphyry_cusps()'s own
    internal quadrant-sizing convention exactly match the specific
    variable relationships (acmc, q1, s1, s4) the C source uses for
    Sripati specifically -- and those two independently-built pieces of
    code disagreed on quadrant handling in a way that was hard to
    reconcile with full confidence. Implementing Sripati's 6 explicit
    points directly from the source's own formulas sidesteps that
    reconciliation problem entirely: there's only one implementation to
    trust, not two that need to agree.

    acmc = the signed short arc from MC to Ascendant (same quantity
    established and validated while building true Placidus). Houses
    4-9 are the standard +180 antipodal mirrors of 10-12 and 1-3,
    applied the same way the C source applies it for every house
    system.
    """
    asc, mc = sidereal_ascendant, sidereal_mc

    acmc = norm360(asc - mc)
    if acmc > 180.0:
        acmc -= 360.0
    if acmc < 0.0:
        # Direct transcription of the real source's own correction: this
        # triggers whenever acmc<0, not only at extreme latitudes despite
        # the source's comment suggesting otherwise -- confirmed by
        # testing an ordinary mid-latitude chart that hit this exact
        # condition and needed it to satisfy antipodal + sign-consistency
        # checks simultaneously.
        asc = norm360(asc + 180.0)
        acmc = norm360(asc - mc)
        if acmc > 180.0:
            acmc -= 360.0
    q1 = 180.0 - acmc
    s1 = q1 / 3.0
    s4 = acmc / 3.0

    h1 = norm360(asc - s4 * 0.5)
    h2 = norm360(asc + s1 * 0.5)
    h3 = norm360(asc + s1 * 1.5)
    h10 = norm360(mc - s1 * 0.5)
    h11 = norm360(mc + s4 * 0.5)
    h12 = norm360(mc + s4 * 1.5)

    h4, h5, h6 = norm360(h10 + 180), norm360(h11 + 180), norm360(h12 + 180)
    h7, h8, h9 = norm360(h1 + 180), norm360(h2 + 180), norm360(h3 + 180)

    return [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12]


def house_of_longitude(sidereal_longitude: float, cusps: list) -> int:
    lon = norm360(sidereal_longitude)
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        arc = (end - start) % 360
        offset = (lon - start) % 360
        if offset < arc or arc == 0:
            return i + 1
    return 12

# -- True Placidus (iterative semi-arc trisection) -----------------------
#
# SOURCING AND DEBUGGING HISTORY (kept here because it explains real
# bugs that were found and fixed, not just a citation trail):
#
# Secondary sources disagreed with each other on which house number
# (11 vs 12) pairs with which fraction (1/3 vs 2/3) of the diurnal
# semi-arc, and following the more "authoritative-looking" cluster
# (astro.com's Swiss Ephemeris prose documentation, plus a rigorously
# self-derived third-party article agreeing with it) led to a genuinely
# wrong implementation that was only caught by direct numerical testing.
#
# Two real bugs were found and fixed during development, in this order:
#   1. A sign error: the correct relationship is RA = RAMC - fraction*DSA
#      (subtraction), not addition. Confirmed by converting the
#      independently-validated Ascendant longitude to its own right
#      ascension and checking it against RAMC - DSA(its own declination)
#      -- matched to numerical precision, while the addition form landed
#      on the Descendant instead.
#   2. A flawed validation test: an initial "cusps must always increase
#      in raw degree order" check flagged a false alarm, because which
#      raw direction (increasing or decreasing degrees) is "the short
#      way" between MC and the Ascendant depends on the specific chart
#      (which of the two has the numerically larger longitude) -- this
#      is chart-dependent, not fixed. The corrected test checks that all
#      12 SIGNED SHORT-ARCS between consecutive cusps share the same
#      sign and sum to exactly +-360 deg, which holds regardless of
#      that chart-dependent direction.
#
# The final house-number/fraction pairing (House 11 = 1/3 of DSA, nearer
# MC; House 12 = 2/3, nearer Ascendant; House 3 = 1/3 of NSA, nearer IC;
# House 2 = 2/3, nearer Ascendant) was confirmed against REAL, VERIFIED
# Swiss Ephemeris numeric output (not prose) -- a worked example from an
# independent test suite (Haskell swiss-ephemeris bindings), which
# happened to be a Porphyry-fallback case near the pole but still
# confirms the house-NUMBERING convention, since that convention is
# universal across every quadrant house system: MC < House11 < House12
# < Ascendant, in that source's own numbers, exactly matching what this
# module now produces.
#
# VALIDATION: boundary conditions (fraction=0 gives exactly MC or IC;
# fraction=1 gives exactly the Ascendant) are checked to numerical
# precision. The signed-short-arc and antipodal-pair properties are
# checked across 4 charts spanning both hemispheres, different seasons,
# and different latitudes -- not just the one chart used during
# development. No full external 12-cusp Placidus worked example was
# found to check the final numeric OUTPUT against directly; confidence
# rests on the boundary-condition exactness plus the universal
# numbering convention check, not a end-to-end numeric match.

def _ra_to_ecliptic_longitude(ra_deg: float, obliquity_deg: float) -> float:
    ra = math.radians(ra_deg)
    eps = math.radians(obliquity_deg)
    lon = math.degrees(math.atan2(math.sin(ra), math.cos(ra) * math.cos(eps)))
    return norm360(lon)


def _declination_of_ecliptic_point(longitude_deg: float, obliquity_deg: float) -> float:
    lon = math.radians(longitude_deg)
    eps = math.radians(obliquity_deg)
    return math.degrees(math.asin(math.sin(lon) * math.sin(eps)))


def _diurnal_semi_arc(declination_deg: float, latitude_deg: float) -> float:
    phi = math.radians(latitude_deg)
    dec = math.radians(declination_deg)
    tan_product = max(-0.999999, min(0.999999, math.tan(phi) * math.tan(dec)))
    return 90.0 + math.degrees(math.asin(tan_product))


def _nocturnal_semi_arc(declination_deg: float, latitude_deg: float) -> float:
    return 180.0 - _diurnal_semi_arc(declination_deg, latitude_deg)


def _short_arc_interpolate(start: float, end: float, fraction: float) -> float:
    delta = norm360(end - start)
    if delta > 180.0:
        delta -= 360.0
    return norm360(start + fraction * delta)


def _placidus_diurnal_cusp(ramc_deg: float, latitude_deg: float, obliquity_deg: float,
                            mc_longitude: float, asc_longitude: float,
                            fraction: float, max_iterations: int = 30) -> float:
    lon_guess = _short_arc_interpolate(mc_longitude, asc_longitude, fraction)
    ra = None
    for _ in range(max_iterations):
        lon = lon_guess if ra is None else _ra_to_ecliptic_longitude(ra, obliquity_deg)
        dec = _declination_of_ecliptic_point(lon, obliquity_deg)
        dsa = _diurnal_semi_arc(dec, latitude_deg)
        new_ra = ramc_deg - fraction * dsa
        if ra is not None and abs(norm360(new_ra - ra + 180) - 180) < 1e-8:
            ra = new_ra
            break
        ra = new_ra
    return _ra_to_ecliptic_longitude(ra, obliquity_deg)


def _placidus_nocturnal_cusp(ramc_deg: float, latitude_deg: float, obliquity_deg: float,
                              ic_longitude: float, asc_longitude: float,
                              fraction: float, max_iterations: int = 30) -> float:
    lon_guess = _short_arc_interpolate(ic_longitude, asc_longitude, fraction)
    ra = None
    for _ in range(max_iterations):
        lon = lon_guess if ra is None else _ra_to_ecliptic_longitude(ra, obliquity_deg)
        dec = _declination_of_ecliptic_point(lon, obliquity_deg)
        nsa = _nocturnal_semi_arc(dec, latitude_deg)
        new_ra = ramc_deg + 180.0 + fraction * nsa
        if ra is not None and abs(norm360(new_ra - ra + 180) - 180) < 1e-8:
            ra = new_ra
            break
        ra = new_ra
    return _ra_to_ecliptic_longitude(ra, obliquity_deg)


def placidus_cusps_tropical(epoch: Epoch, latitude_deg: float, longitude_deg: float) -> list:
    """
    True Placidus house cusps (all 12), tropical, via iterative
    semi-arc trisection. Raises ValueError above ~66 deg latitude,
    where the algorithm breaks down (circumpolar regions have no
    well-defined diurnal/nocturnal semi-arc for some ecliptic points) --
    this is a known, universal limitation of Placidus itself, not a bug.
    """
    if abs(latitude_deg) > 66.0:
        raise ValueError(
            "True Placidus cusps are not defined above ~66 deg latitude "
            "(circumpolar regions) -- use Whole Sign, Equal, or Porphyry instead."
        )

    obliquity = float(Coordinates.true_obliquity(epoch))
    nutation = float(Coordinates.nutation_longitude(epoch))
    gst_days = float(epoch.apparent_sidereal_time(obliquity, nutation))
    ramc = norm360(gst_days * 360.0 + longitude_deg)

    asc = ascendant_tropical(epoch, latitude_deg, longitude_deg)
    mc = midheaven_tropical(epoch, longitude_deg)
    ic = norm360(mc + 180)
    desc = norm360(asc + 180)

    house11 = _placidus_diurnal_cusp(ramc, latitude_deg, obliquity, mc, asc, 1.0 / 3.0)
    house12 = _placidus_diurnal_cusp(ramc, latitude_deg, obliquity, mc, asc, 2.0 / 3.0)
    house2 = _placidus_nocturnal_cusp(ramc, latitude_deg, obliquity, ic, asc, 2.0 / 3.0)
    house3 = _placidus_nocturnal_cusp(ramc, latitude_deg, obliquity, ic, asc, 1.0 / 3.0)

    house5 = norm360(house11 + 180)
    house6 = norm360(house12 + 180)
    house8 = norm360(house2 + 180)
    house9 = norm360(house3 + 180)

    return [asc, house2, house3, ic, house5, house6, desc, house8, house9, mc, house11, house12]