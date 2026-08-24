"""Nakshatra (lunar mansion) and pada (quarter) lookup from a sidereal longitude."""

from .constants import NAKSHATRAS, NAKSHATRA_LORDS, DEG_PER_NAKSHATRA, DEG_PER_PADA
from .utils import norm360


def nakshatra_index(sidereal_longitude: float) -> int:
    """0-26 index into NAKSHATRAS."""
    return int(norm360(sidereal_longitude) // DEG_PER_NAKSHATRA)


def pada(sidereal_longitude: float) -> int:
    """1-4, the quarter of the nakshatra."""
    lon = norm360(sidereal_longitude)
    position_in_nakshatra = lon % DEG_PER_NAKSHATRA
    return int(position_in_nakshatra // DEG_PER_PADA) + 1


def nakshatra_info(sidereal_longitude: float) -> dict:
    idx = nakshatra_index(sidereal_longitude)
    return {
        "name": NAKSHATRAS[idx],
        "index": idx,
        "lord": NAKSHATRA_LORDS[idx],
        "pada": pada(sidereal_longitude),
        "degrees_into_nakshatra": round(norm360(sidereal_longitude) % DEG_PER_NAKSHATRA, 4),
    }
