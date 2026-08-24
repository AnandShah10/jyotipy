"""
BirthChart: the main entry point. Computes a full sidereal Vedic chart
from a birth datetime + location, and exposes everything else in the
package (nakshatras, houses, vargas, dashas, yogas, panchanga) as methods
so a typical usage looks like:

    from jyotipy import BirthChart
    from datetime import datetime

    chart = BirthChart(
        dt=datetime(1990, 6, 15, 14, 32),
        utc_offset_hours=5.5,
        latitude=23.03, longitude=72.58,   # Ahmedabad
    )
    print(chart.positions)          # {Graha: sidereal_longitude}
    print(chart.ascendant)          # sidereal longitude
    print(chart.houses("whole_sign"))
    print(chart.varga("D9"))        # {Graha: varga_sign_index}
    print(chart.mahadashas())
    print(chart.yogas())
"""

from datetime import datetime

from . import ephemeris, houses as houses_mod, varga as varga_mod
from . import dasha as dasha_mod, yogas as yogas_mod, panchanga as panchanga_mod
from .ayanamsa import AyanamsaSystem, get_ayanamsa, tropical_to_sidereal
from .constants import Graha, SIGNS
from .nakshatra import nakshatra_info
from .utils import sign_index, degree_in_sign, norm360


class BirthChart:
    def __init__(self, dt: datetime, utc_offset_hours: float,
                 latitude: float, longitude: float,
                 ayanamsa: AyanamsaSystem = AyanamsaSystem.LAHIRI,
                 use_true_node: bool = False):
        self.dt = dt
        self.utc_offset_hours = utc_offset_hours
        self.latitude = latitude
        self.longitude = longitude
        self.ayanamsa_system = ayanamsa

        self.epoch = ephemeris.epoch_from_datetime(dt, utc_offset_hours)
        self.ayanamsa_value = get_ayanamsa(self.epoch, ayanamsa)

        self._tropical_positions = ephemeris.tropical_longitudes(
            self.epoch, true_node=use_true_node)
        self.positions = {
            g: tropical_to_sidereal(lon, self.epoch, ayanamsa)
            for g, lon in self._tropical_positions.items()
        }

        asc_tropical = houses_mod.ascendant_tropical(self.epoch, latitude, longitude)
        mc_tropical = houses_mod.midheaven_tropical(self.epoch, longitude)
        self.ascendant = tropical_to_sidereal(asc_tropical, self.epoch, ayanamsa)
        self.midheaven = tropical_to_sidereal(mc_tropical, self.epoch, ayanamsa)

    # -- Signs / degrees -------------------------------------------------

    def sign_of(self, graha: Graha) -> str:
        return SIGNS[sign_index(self.positions[graha])]

    def degree_of(self, graha: Graha) -> float:
        return degree_in_sign(self.positions[graha])

    def summary(self) -> dict:
        return {
            g.value: {
                "longitude": round(lon, 4),
                "sign": SIGNS[sign_index(lon)],
                "degree_in_sign": round(degree_in_sign(lon), 4),
                **nakshatra_info(lon),
            }
            for g, lon in self.positions.items()
        }

    # -- Houses ------------------------------------------------------------

    def houses(self, system: str = "whole_sign") -> list:
        """Return the 12 house cusps (sidereal longitudes) for the given
        system: 'whole_sign', 'equal', or 'porphyry'."""
        if system == "whole_sign":
            return houses_mod.whole_sign_cusps(self.ascendant)
        elif system == "equal":
            return houses_mod.equal_house_cusps(self.ascendant)
        elif system == "porphyry":
            return houses_mod.porphyry_cusps(self.ascendant, self.midheaven)
        raise ValueError(f"Unknown house system: {system!r}")

    def house_of(self, graha: Graha, system: str = "whole_sign") -> int:
        cusps = self.houses(system)
        return houses_mod.house_of_longitude(self.positions[graha], cusps)

    # -- Divisional charts ---------------------------------------------

    def varga(self, division: str) -> dict:
        """{Graha: varga_sign_index} for a division like 'D9'. Also
        includes the ascendant under the key 'Ascendant'. Raises
        NotImplementedError for divisions beyond D12 -- see varga.py."""
        result = {g: varga_mod.varga_sign(lon, division) for g, lon in self.positions.items()}
        result["Ascendant"] = varga_mod.varga_sign(self.ascendant, division)
        return result

    # -- Dasha -----------------------------------------------------------

    def mahadashas(self, cycles: int = 1) -> list:
        moon_lon = self.positions[Graha.MOON]
        return dasha_mod.mahadasha_sequence(moon_lon, self.epoch.jde(), cycles=cycles)

    def antardashas(self, mahadasha_period: dict) -> list:
        return dasha_mod.antardasha_sequence(mahadasha_period)

    # -- Yogas -------------------------------------------------------------

    def yogas(self) -> dict:
        return yogas_mod.detect_all_yogas(self.positions, self.ascendant)

    # -- Panchanga ---------------------------------------------------------

    def panchanga(self) -> dict:
        sun_trop = self._tropical_positions[Graha.SUN]
        moon_trop = self._tropical_positions[Graha.MOON]
        moon_sid = self.positions[Graha.MOON]
        return panchanga_mod.full_panchanga(sun_trop, moon_trop, moon_sid, self.dt)
