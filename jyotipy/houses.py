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

House systems implemented in v0.1:
  - Whole Sign (Rashi-based): the sign containing the ascendant IS the
    1st house, full 30 deg. This is the default/primary system in most
    Jyotish traditions and is what most Vedic software uses out of the box.
  - Equal House: 12 cusps, each exactly 30 deg apart starting at the
    ascendant's exact degree (not snapped to the sign boundary).
  - Porphyry (quadrant trisection): cusps 1/4/7/10 = Asc/IC/Desc/MC,
    intermediate cusps trisect each quadrant's arc. This is what's
    commonly (and loosely) called "Sripati" in a lot of Vedic software,
    but true Sripati and true Placidus both require iteratively solving
    the diurnal/nocturnal semi-arc equations -- not implemented yet, see
    README roadmap. Don't rely on this for Placidus/Sripati-sensitive
    KP sub-lord work.
"""

from pymeeus.Epoch import Epoch
from pymeeus import Coordinates
import math

from .utils import norm360


def ascendant_tropical(epoch: Epoch, latitude_deg: float, longitude_deg: float) -> float:
    """
    Tropical ecliptic longitude of the Ascendant (rising degree), in degrees.

    latitude_deg: geographic latitude, +N / -S.
    longitude_deg: geographic longitude, +E / -W.
    """
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
    """Tropical ecliptic longitude of the Midheaven (MC), in degrees."""
    obliquity = float(Coordinates.true_obliquity(epoch))
    nutation = float(Coordinates.nutation_longitude(epoch))
    gst_days = float(epoch.apparent_sidereal_time(obliquity, nutation))
    ramc = norm360(gst_days * 360.0 + longitude_deg)

    theta = math.radians(ramc)
    eps = math.radians(obliquity)
    mc = math.degrees(math.atan2(math.sin(theta), math.cos(theta) * math.cos(eps)))
    return norm360(mc)


def whole_sign_cusps(sidereal_ascendant: float) -> list:
    """
    12 house cusps under the Whole Sign system: house 1 starts at 0 deg of
    the ascendant's sign, and each subsequent house is the next full sign.
    """
    asc_sign_start = (int(sidereal_ascendant // 30)) * 30
    return [norm360(asc_sign_start + 30 * i) for i in range(12)]


def equal_house_cusps(sidereal_ascendant: float) -> list:
    """12 cusps, each exactly 30 deg from the last, starting at the exact
    ascendant degree (not snapped to a sign boundary)."""
    return [norm360(sidereal_ascendant + 30 * i) for i in range(12)]


def porphyry_cusps(sidereal_ascendant: float, sidereal_mc: float) -> list:
    """
    Quadrant-based cusps: 1=Asc, 10=MC, 7=Asc+180, 4=MC+180, with the
    remaining cusps trisecting each quadrant arc.
    """
    asc, mc = sidereal_ascendant, sidereal_mc
    ic = norm360(mc + 180)
    desc = norm360(asc + 180)

    def trisect(start, end, n=3):
        arc = (end - start) % 360
        return [norm360(start + arc * k / n) for k in range(n)]

    q1 = trisect(asc, ic)      # houses 1,2,3
    q2 = trisect(ic, desc)     # houses 4,5,6
    q3 = trisect(desc, mc)     # houses 7,8,9
    q4 = trisect(mc, asc)      # houses 10,11,12
    return q1 + q2 + q3 + q4


def house_of_longitude(sidereal_longitude: float, cusps: list) -> int:
    """Given a list of 12 ascending house cusps, return which house (1-12)
    a sidereal longitude falls into."""
    lon = norm360(sidereal_longitude)
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        arc = (end - start) % 360
        offset = (lon - start) % 360
        if offset < arc or arc == 0:
            return i + 1
    return 12  # fallback, shouldn't normally hit
