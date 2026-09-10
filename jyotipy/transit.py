"""
Gochara (transit) analysis: evaluates where the planets are RIGHT NOW
relative to a natal chart's Moon sign (Janma Rasi) -- the classical
reference point for transit analysis, not the Ascendant (see module
docstring reasoning in the sourced material below).

SOURCING: the good/bad-house table and the Vedha (obstruction) table are
both taken from a modern chapter-by-chapter guide to B.V. Raman's own
"Hindu Predictive Astrology" (Chapter 34), which quotes Raman's text
directly rather than paraphrasing. Sun, Moon, Saturn, and Venus's tables
are additionally cross-checked against a second, independent source and
match exactly. Mars, Mercury, and Jupiter's tables come only from the
Raman-chapter source, but are internally consistent between that source's
summary table and its separate detailed 12-house breakdown -- so at least
self-consistent even without a second external source.

ONE KNOWN DISCREPANCY: a secondary source lists Jupiter's good houses as
{2,5,7,9} (4 houses); the primary source used here lists {2,5,7,9,11} (5
houses) and is internally consistent about it (its own detailed
house-by-house table separately confirms the 11th as good). Implemented
per the primary source; flagged here rather than silently resolved.

ONE SOURCE-DOCUMENTED AMBIGUITY: the primary source itself presents
Jupiter's Vedha point for its 11th house as "4 (or 8)" -- an alternate
reading it doesn't resolve. Implemented as 4 (matching the more common
convention elsewhere in the same table), with 8 as a documented
alternate -- not silently picked.

ASHTAKAVARGA BINDU QUALIFICATION: per the same primary source, a
transited sign needs 4 or more Bhinnashtakavarga bindus to deliver its
full effect (below 4 is weak) -- this threshold is used in
transit_report()'s bindu_qualifies field. An earlier version of this
module used an unsourced >=5 threshold as a rough guess; that's been
corrected to the properly-sourced >=4 figure.

Rahu and Ketu are not covered by classical Gochara tables in their own
right; the source explicitly states "Rahu transiting produces results
similar to those of Saturn, and Ketu to those of Mars" -- implemented as
a direct alias to those tables, not an independent ruleset.
"""

from datetime import datetime

from .constants import Graha
from .utils import sign_index, norm360
from . import ephemeris as ephemeris_mod
from .ayanamsa import AyanamsaSystem, get_ayanamsa, tropical_to_sidereal
from . import ashtakavarga as ashtakavarga_mod

GOOD_HOUSES_FROM_MOON = {
    Graha.SUN: {3, 6, 10, 11},
    Graha.MOON: {1, 3, 6, 7, 10, 11},
    Graha.MARS: {3, 6, 10, 11},
    Graha.MERCURY: {2, 4, 6, 8, 10, 11},
    Graha.JUPITER: {2, 5, 7, 9, 11},
    Graha.VENUS: {1, 2, 3, 4, 5, 8, 9, 11, 12},
    Graha.SATURN: {3, 6, 11},
}
# Per Raman: Rahu follows Saturn's pattern, Ketu follows Mars's.
GOOD_HOUSES_FROM_MOON[Graha.RAHU] = GOOD_HOUSES_FROM_MOON[Graha.SATURN]
GOOD_HOUSES_FROM_MOON[Graha.KETU] = GOOD_HOUSES_FROM_MOON[Graha.MARS]

# VEDHA[planet][good_house] = obstruction house. If ANY other planet
# (subject to the exceptions below) occupies the obstruction house from
# Moon while `planet` is in `good_house` from Moon, planet's good result
# is blocked.
VEDHA = {
    Graha.SUN: {11: 5, 3: 9, 10: 4, 6: 12},
    Graha.MOON: {7: 2, 1: 5, 6: 12, 11: 8, 10: 4, 3: 9},
    Graha.MARS: {3: 12, 11: 5, 6: 9},
    Graha.MERCURY: {2: 5, 4: 3, 6: 9, 8: 1, 10: 7, 11: 12},
    Graha.JUPITER: {2: 12, 11: 4, 9: 10, 5: 3, 7: 3},  # 11's vedha: source says "4 (or 8)", using 4
    Graha.VENUS: {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    Graha.SATURN: {3: 12, 11: 5, 6: 9},
}
VEDHA[Graha.RAHU] = VEDHA[Graha.SATURN]
VEDHA[Graha.KETU] = VEDHA[Graha.MARS]

# Documented exceptions: these pairs never obstruct each other, in either
# direction, regardless of what the VEDHA table above says.
_NO_VEDHA_PAIRS = {
    frozenset({Graha.SUN, Graha.SATURN}),
    frozenset({Graha.MOON, Graha.MERCURY}),
}


def house_from_moon(transit_sign: int, moon_sign: int) -> int:
    """1-12, counted inclusively from the natal Moon's sign."""
    return ((transit_sign - moon_sign) % 12) + 1


def is_good_house(planet: Graha, house: int) -> bool:
    return house in GOOD_HOUSES_FROM_MOON[planet]


def check_vedha(planet: Graha, house: int, other_transit_signs: dict, moon_sign: int) -> bool:
    """
    True if `planet`'s good result in `house` (from Moon) is obstructed.
    other_transit_signs: {Graha: current_sidereal_sign_index} for every
    OTHER currently-transiting planet to check against.
    """
    vedha_house = VEDHA.get(planet, {}).get(house)
    if vedha_house is None:
        return False  # this house has no defined vedha point for this planet
    for other_planet, other_sign in other_transit_signs.items():
        if other_planet == planet:
            continue
        if frozenset({planet, other_planet}) in _NO_VEDHA_PAIRS:
            continue
        if house_from_moon(other_sign, moon_sign) == vedha_house:
            return True
    return False


def current_sidereal_positions(dt: datetime, utc_offset_hours: float,
                                ayanamsa: AyanamsaSystem = AyanamsaSystem.LAHIRI,
                                true_node: bool = False) -> dict:
    """Sidereal longitudes for all 9 grahas AT THE TRANSIT MOMENT -- uses
    the ayanamsa evaluated at the transit epoch, not the birth epoch,
    since ayanamsa itself drifts slowly over time."""
    epoch = ephemeris_mod.epoch_from_datetime(dt, utc_offset_hours)
    tropical = ephemeris_mod.tropical_longitudes(epoch, true_node=true_node)
    return {g: tropical_to_sidereal(lon, epoch, ayanamsa) for g, lon in tropical.items()}


def transit_report(natal_moon_longitude: float, natal_positions_for_ashtakavarga: dict,
                    natal_ascendant: float, transit_dt: datetime,
                    transit_utc_offset_hours: float = 0.0,
                    ayanamsa: AyanamsaSystem = AyanamsaSystem.LAHIRI) -> dict:
    """
    Full Gochara report for the 7 classical grahas + Rahu/Ketu, evaluated
    at transit_dt against a natal chart's Moon sign.

    natal_positions_for_ashtakavarga / natal_ascendant: the NATAL chart's
    values, needed to look up each planet's own Bhinnashtakavarga bindu
    count at its current transit sign (per Raman: transit results can't
    be judged accurately without this).
    """
    moon_sign = sign_index(natal_moon_longitude)
    transit_positions = current_sidereal_positions(transit_dt, transit_utc_offset_hours, ayanamsa)
    transit_signs = {g: sign_index(lon) for g, lon in transit_positions.items()}

    # Ashtakavarga is only defined for the 7 classical grahas (not
    # Rahu/Ketu) per Parashari convention -- see ashtakavarga.py.
    bav_cache = {
        p: ashtakavarga_mod.bhinnashtakavarga(p, natal_positions_for_ashtakavarga, natal_ascendant)
        for p in ashtakavarga_mod.BAV_PLANETS
    }

    report = {}
    for planet in [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                   Graha.JUPITER, Graha.VENUS, Graha.SATURN, Graha.RAHU, Graha.KETU]:
        t_sign = transit_signs[planet]
        house = house_from_moon(t_sign, moon_sign)
        good = is_good_house(planet, house)
        vedha_active = good and check_vedha(planet, house, transit_signs, moon_sign)
        bindus = bav_cache[planet][t_sign] if planet in bav_cache else None
        # Threshold per Raman (Ch. 34, via a cross-validated secondary
        # guide already used elsewhere in this module): 4 or more bindus
        # in the transited sign qualifies a transit to deliver its full
        # effect; below 4 is weak, regardless of the raw good/bad house
        # verdict.
        bindu_qualifies = bindus is not None and bindus >= 4

        if good and not vedha_active:
            verdict = "good" if bindu_qualifies or bindus is None else "good house, but low Ashtakavarga bindus weaken it"
        elif good and vedha_active:
            verdict = "good house, but obstructed (Vedha) -- treat as neutral/weak, not good"
        else:
            verdict = "bad"
            if bindu_qualifies:
                verdict += " (but adequate Ashtakavarga bindus somewhat mitigate this)"

        report[planet.value] = {
            "house_from_moon": house,
            "classically_good_house": good,
            "vedha_obstruction": vedha_active,
            "ashtakavarga_bindus_here": bindus,
            "bindu_qualifies": bindu_qualifies,
            "verdict": verdict,
        }
    return report


def sade_sati_status(saturn_sidereal_longitude: float, natal_moon_longitude: float) -> dict:
    """
    Sade Sati: Saturn transiting the 12th, 1st, or 2nd sign from the
    natal Moon (a combined ~7.5 year period). Also flags Kantaka Sani
    (Saturn in the 4th from Moon) and Ashtama Sani (Saturn in the 8th
    from Moon) -- two other named, specifically Saturn-from-Moon
    caution periods documented in the same source.
    """
    moon_sign = sign_index(natal_moon_longitude)
    saturn_sign = sign_index(saturn_sidereal_longitude)
    house = house_from_moon(saturn_sign, moon_sign)

    in_sade_sati = house in (12, 1, 2)
    phase = None
    if house == 12:
        phase = "rising (1st phase)"
    elif house == 1:
        phase = "peak (2nd phase)"
    elif house == 2:
        phase = "setting (3rd phase)"

    return {
        "house_from_moon": house,
        "sade_sati": in_sade_sati,
        "phase": phase,
        "kantaka_sani": house == 4,
        "ashtama_sani": house == 8,
    }