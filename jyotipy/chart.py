"""BirthChart: the main entry point."""

from datetime import datetime

from . import ephemeris, houses as houses_mod, varga as varga_mod
from . import dasha as dasha_mod, yogas as yogas_mod, panchanga as panchanga_mod
from . import ashtakavarga as ashtakavarga_mod
from . import transit as transit_mod
from . import shadbala as shadbala_mod
from . import dashabhukti as dashabhukti_mod
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

    def houses(self, system: str = "whole_sign") -> list:
        if system == "whole_sign":
            return houses_mod.whole_sign_cusps(self.ascendant)
        elif system == "equal":
            return houses_mod.equal_house_cusps(self.ascendant)
        elif system == "porphyry":
            return houses_mod.porphyry_cusps(self.ascendant, self.midheaven)
        elif system == "placidus":
            tropical_cusps = houses_mod.placidus_cusps_tropical(self.epoch, self.latitude, self.longitude)
            return [tropical_to_sidereal(lon, self.epoch, self.ayanamsa_system) for lon in tropical_cusps]
        elif system == "sripati":
            tropical_cusps = houses_mod.sripati_cusps(self.ascendant_tropical_value, self.midheaven_tropical_value)
            # or, if chart.py only stores sidereal ascendant/midheaven directly:
            tropical_cusps = houses_mod.sripati_cusps(
                houses_mod.ascendant_tropical(self.epoch, self.latitude, self.longitude),
                houses_mod.midheaven_tropical(self.epoch, self.longitude),
            )
            return [tropical_to_sidereal(lon, self.epoch, self.ayanamsa_system) for lon in tropical_cusps]
        raise ValueError(f"Unknown house system: {system!r}")

    def house_of(self, graha: Graha, system: str = "whole_sign") -> int:
        cusps = self.houses(system)
        return houses_mod.house_of_longitude(self.positions[graha], cusps)

    def varga(self, division: str) -> dict:
        result = {g: varga_mod.varga_sign(lon, division) for g, lon in self.positions.items()}
        result["Ascendant"] = varga_mod.varga_sign(self.ascendant, division)
        return result

    def mahadashas(self, cycles: int = 1) -> list:
        moon_lon = self.positions[Graha.MOON]
        return dasha_mod.mahadasha_sequence(moon_lon, self.epoch.jde(), cycles=cycles)

    def antardashas(self, mahadasha_period: dict) -> list:
        return dasha_mod.antardasha_sequence(mahadasha_period)

    def yogas(self) -> dict:
        return yogas_mod.detect_all_yogas(self.positions, self.ascendant)

    def ashtakavarga(self, planet: Graha = None) -> dict:
        """Bhinnashtakavarga for one planet (0-11 bindu list, Aries-first)
        if `planet` is given, otherwise every planet's BAV plus the
        Sarvashtakavarga in one dict (see ashtakavarga.py)."""
        if planet is not None:
            return ashtakavarga_mod.bhinnashtakavarga(planet, self.positions, self.ascendant)
        return ashtakavarga_mod.full_ashtakavarga(self.positions, self.ascendant)

    def reduced_ashtakavarga(self, planet: Graha) -> list:
        """Bhinnashtakavarga for `planet` after Trikona Sodhana and
        Ekadhipatya Sodhana (in that fixed order) -- see ashtakavarga.py
        for the sourcing on these two reduction techniques."""
        return ashtakavarga_mod.reduced_bhinnashtakavarga(planet, self.positions, self.ascendant)

    def _is_moon_waxing(self) -> bool:
        return self.panchanga()["tithi"]["paksha"] == "Shukla"

    def shadbala(self, planet: Graha) -> dict:
        """Shadbala report for one planet -- see shadbala.py for exactly
        what's implemented. NOTE: this single-planet call omits Yuddha
        Bala's mutual adjustment (it needs to compare two planets head
        to head) -- use full_shadbala() for a war-adjusted, fully
        consistent set."""
        navamsha_sign = varga_mod.d9_navamsha(self.positions[planet])
        house = self.house_of(planet, system="whole_sign")
        classical_positions = {g: lon for g, lon in self.positions.items()
                                if g in (Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                                         Graha.JUPITER, Graha.VENUS, Graha.SATURN)}
        return shadbala_mod.shadbala_report(
            planet, self.positions[planet], navamsha_sign, house,
            self.ascendant, self.midheaven, classical_positions,
            self._tropical_positions, self.dt, self.utc_offset_hours,
            self.latitude, self.longitude, self.ayanamsa_system,
            birth_epoch=self.epoch, moon_is_waxing=self._is_moon_waxing(),
        )

    def full_shadbala(self) -> dict:
        """Shadbala for all 7 classical grahas at once, WITH Yuddha
        Bala's mutual war adjustment correctly applied -- the complete,
        internally consistent version. Prefer this over calling
        shadbala() once per planet whenever Yuddha Bala matters."""
        classical = [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                     Graha.JUPITER, Graha.VENUS, Graha.SATURN]
        classical_positions = {g: lon for g, lon in self.positions.items() if g in classical}
        navamsha_signs = {g: varga_mod.d9_navamsha(self.positions[g]) for g in classical}
        houses_from_ascendant = {g: self.house_of(g, system="whole_sign") for g in classical}

        return shadbala_mod.full_shadbala_for_chart(
            classical_positions, self._tropical_positions,
            self.ascendant, self.midheaven, self.dt, self.utc_offset_hours,
            self.latitude, self.longitude, self.ayanamsa_system, self.epoch,
            navamsha_signs, houses_from_ascendant,
            moon_is_waxing=self._is_moon_waxing(),
        )

    def transits(self, transit_dt, transit_utc_offset_hours: float = 0.0) -> dict:
        """Full Gochara report for the given moment, evaluated against
        this chart's natal Moon and Ashtakavarga. See transit.py for the
        sourcing and honesty notes on the underlying classical tables."""
        return transit_mod.transit_report(
            natal_moon_longitude=self.positions[Graha.MOON],
            natal_positions_for_ashtakavarga=self.positions,
            natal_ascendant=self.ascendant,
            transit_dt=transit_dt,
            transit_utc_offset_hours=transit_utc_offset_hours,
            ayanamsa=self.ayanamsa_system,
        )

    def dasha_bhukti_activation(self, at_dt=None) -> dict:
        """
        Which of the currently-active Mahadasha and Antardasha lords
        actually dominates the period's results, per Raman's own stated
        method (compare their Shadbala; the stronger one's significations
        predominate), plus whether each clears its own minimum Shadbala
        threshold. See dashabhukti.py for full sourcing.

        at_dt: defaults to this chart's own birth moment if omitted --
        pass a later datetime to judge a currently-running period for
        someone born in the past.
        """
        at_dt = at_dt or self.dt
        lords = dashabhukti_mod.current_dasha_bhukti_lords(
            self.mahadashas(cycles=2), self.antardashas, at_dt)
        if lords["mahadasha"] is None:
            return {"error": "at_dt falls outside the computed dasha range -- "
                              "try chart.mahadashas(cycles=N) with a larger N."}

        dasha_lord = lords["mahadasha"]["lord"]
        bhukti_lord = lords["antardasha"]["lord"] if lords["antardasha"] else dasha_lord

        dasha_shadbala = self.shadbala(dasha_lord)["partial_total_virupas"]
        bhukti_shadbala = self.shadbala(bhukti_lord)["partial_total_virupas"]

        result = dashabhukti_mod.dasha_bhukti_dominance(
            dasha_lord, dasha_shadbala, bhukti_lord, bhukti_shadbala)
        result["mahadasha_period"] = lords["mahadasha"]
        result["antardasha_period"] = lords["antardasha"]
        return result

    def sade_sati(self, transit_dt, transit_utc_offset_hours: float = 0.0) -> dict:
        """Sade Sati / Kantaka Sani / Ashtama Sani status for the given
        moment, based on Saturn's transit relative to this chart's Moon."""
        positions_now = transit_mod.current_sidereal_positions(
            transit_dt, transit_utc_offset_hours, self.ayanamsa_system)
        return transit_mod.sade_sati_status(positions_now[Graha.SATURN], self.positions[Graha.MOON])

    def panchanga(self) -> dict:
        sun_trop = self._tropical_positions[Graha.SUN]
        moon_trop = self._tropical_positions[Graha.MOON]
        moon_sid = self.positions[Graha.MOON]
        return panchanga_mod.full_panchanga(sun_trop, moon_trop, moon_sid, self.dt)