"""
Tropical geocentric longitudes for the 9 grahas, computed from pymeeus
(VSOP87 for the Sun and major planets, ELP2000-82 for the Moon).

This module deliberately outputs TROPICAL longitudes only. Sidereal
conversion (subtracting the ayanamsa) happens one layer up in chart.py --
keeping ephemeris.py ayanamsa-agnostic means switching ayanamsa systems,
or swapping this backend for a different ephemeris later, never touches
astrology-layer code.

Rahu/Ketu (the lunar nodes) are not physical bodies with VSOP87 orbits --
they're computed directly from the Moon's orbital node longitude, which
pymeeus provides. We default to the MEAN node (the classical/Parashari
standard) with the TRUE node available as an option.
"""

from datetime import datetime
from pymeeus.Epoch import Epoch
from pymeeus.Sun import Sun
from pymeeus.Moon import Moon
from pymeeus.Mercury import Mercury
from pymeeus.Venus import Venus
from pymeeus.Mars import Mars
from pymeeus.Jupiter import Jupiter
from pymeeus.Saturn import Saturn
from pymeeus import Coordinates

from .constants import Graha
from .utils import norm360, to_utc_epoch

_PLANET_CLASSES = {
    Graha.MERCURY: Mercury,
    Graha.VENUS: Venus,
    Graha.MARS: Mars,
    Graha.JUPITER: Jupiter,
    Graha.SATURN: Saturn,
}


def _planet_tropical_longitude(graha: Graha, epoch: Epoch) -> float:
    """Geocentric ecliptic longitude for a planet, via RA/Dec -> ecliptic
    conversion (pymeeus's geocentric_position returns equatorial coords)."""
    cls = _PLANET_CLASSES[graha]
    ra, dec, _elongation = cls.geocentric_position(epoch)
    obliquity = Coordinates.true_obliquity(epoch)
    lon, _lat = Coordinates.equatorial2ecliptical(ra, dec, obliquity)
    return norm360(float(lon))


def _sun_tropical_longitude(epoch: Epoch) -> float:
    lon, _lat, _r = Sun.apparent_geocentric_position(epoch)
    return norm360(float(lon))


def _moon_tropical_longitude(epoch: Epoch) -> float:
    lon, _lat, _dist, _parallax = Moon.apparent_ecliptical_pos(epoch)
    return norm360(float(lon))


def _rahu_tropical_longitude(epoch: Epoch, true_node: bool = False) -> float:
    if true_node:
        node = Moon.longitude_true_ascending_node(epoch)
    else:
        node = Moon.longitude_mean_ascending_node(epoch)
    return norm360(float(node))


def tropical_longitudes(epoch: Epoch, true_node: bool = False) -> dict:
    """
    Return {Graha: tropical_ecliptic_longitude_degrees} for all 9 grahas.

    true_node: use the oscillating true lunar node instead of the smoothed
    mean node for Rahu/Ketu. Most classical Vedic technique (Vimshottari
    dasha, standard yogas) assumes the MEAN node -- only switch this if
    you specifically know your tradition/software uses the true node.
    """
    positions = {
        Graha.SUN: _sun_tropical_longitude(epoch),
        Graha.MOON: _moon_tropical_longitude(epoch),
    }
    for graha in _PLANET_CLASSES:
        positions[graha] = _planet_tropical_longitude(graha, epoch)

    rahu = _rahu_tropical_longitude(epoch, true_node=true_node)
    positions[Graha.RAHU] = rahu
    positions[Graha.KETU] = norm360(rahu + 180.0)
    return positions


def epoch_from_datetime(dt: datetime, utc_offset_hours: float = 0.0) -> Epoch:
    """Convenience re-export so callers only need to import from one place."""
    return to_utc_epoch(dt, utc_offset_hours)
