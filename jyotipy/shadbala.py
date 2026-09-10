"""
Shadbala: the six-fold planetary strength system from BPHS Ch. 27-39,
measured in Virupas (60 Virupas = 1 Rupa).

HONEST SCOPE -- read this before trusting any total. Shadbala has SIX
components, and Sthana Bala alone has FIVE sub-components. This module
implements the parts with unambiguous, cross-sourced formulas and
explicitly does NOT implement the parts that require large, contested
lookup tables -- following the same principle as varga.py and
ashtakavarga.py: verified or flagged, never guessed.

IMPLEMENTED:
  - Naisargika Bala (natural strength) -- fixed constants, 3 independent
    sources agree exactly.
  - Dig Bala (directional strength) -- formula-based, cross-sourced.
  - Sthana Bala, ALL 5 classical sub-components (see saptavargaja.py for
    the largest and riskiest one's extensive sourcing notes).
  - Kala Bala, ALL 6 sub-components: Nathonnata Bala, Paksha Bala,
    Tribhaga Bala, Ayana Bala, Varsha+Masa+Dina+Hora Bala, and Yuddha
    Bala -- see kalabala.py and yuddhabala.py for full sourcing.
  - Chesta Bala, for ALL 7 classical grahas. Sun and Moon use BPHS's
    explicit substitution rule ("Sun's Chesta Bala will correspond to
    his Ayana Bala. Moon's Paksha Bala will itself be her Chesta
    Bala"). The other 5 (Mars, Mercury, Jupiter, Venus, Saturn) use the
    actual motion-based formula, validated against the real-world,
    independently documented 2020 Mars retrograde period.
  - Drik Bala (aspectual strength) -- see drikbala.py. The continuous
    "Aspect Pinda" formula was reconstructed from a fully worked 30x12
    reference grid found in a primary-adjacent source and validated
    against that source's own worked example (Jupiter aspecting the Sun
    from 192 deg away scores exactly +13.5) plus 4 more independent
    spot-checks from the same grid.

Shadbala is therefore now COMPLETE across all six components. Two
honest caveats remain, though, worth reading before treating any total
as gospel:
  - Yuddha Bala only resolves mutually across a FULL set of planets
    (it needs to compare two planets' Tri-bala head to head), so it is
    NOT available from shadbala_report() called on one planet in
    isolation -- use full_shadbala_for_chart() for a complete, mutually
    consistent set. shadbala_report() alone omits Yuddha Bala's
    adjustment even when a war is present.
  - Some individual formulas carry noted uncertainty even though
    implemented (see kalabala.py, saptavargaja.py, yuddhabala.py, and
    drikbala.py module docstrings for the specific caveats on each --
    e.g. Yuddha Bala's victor rule doesn't implement the secondary
    "Venus always wins" exception some sources describe). This is a
    working, well-sourced Shadbala, not a claim of textual perfection.
"""

from datetime import datetime

from .constants import Graha
from .utils import sign_index, degree_in_sign, norm360
from . import saptavargaja as saptavargaja_mod
from . import kalabala as kalabala_mod
from . import drikbala as drikbala_mod
from . import yuddhabala as yuddhabala_mod

# -- Naisargika Bala: fixed constants, 3 independent sources agree exactly.
NAISARGIKA_BALA = {
    Graha.SUN: 60.0, Graha.MOON: 51.43, Graha.VENUS: 42.86,
    Graha.JUPITER: 34.29, Graha.MERCURY: 25.71, Graha.MARS: 17.14,
    Graha.SATURN: 8.57,
}

# Exact exaltation degrees (sign_index, degree_in_sign). Debilitation is
# always the opposite sign at the same degree. Sun's value cross-checked
# against 2 independent worked examples; the rest are extremely
# standard, widely repeated values.
EXALTATION_POINT = {
    Graha.SUN: (0, 10.0),      # 10 deg Aries
    Graha.MOON: (1, 3.0),      # 3 deg Taurus
    Graha.MARS: (9, 28.0),     # 28 deg Capricorn
    Graha.MERCURY: (5, 15.0),  # 15 deg Virgo
    Graha.JUPITER: (3, 5.0),   # 5 deg Cancer
    Graha.VENUS: (11, 27.0),   # 27 deg Pisces
    Graha.SATURN: (6, 20.0),   # 20 deg Libra
}

MALE_PLANETS = {Graha.SUN, Graha.MARS, Graha.JUPITER}
FEMALE_PLANETS = {Graha.MOON, Graha.VENUS}
NEUTRAL_PLANETS = {Graha.MERCURY, Graha.SATURN}

# Dig Bala: strongest house (from Lagna) per planet. Cross-checked
# against 2 sources; one lower-quality source disagreed on Jupiter
# (claimed 9th instead of 1st) and is treated as an outlier here since
# it conflicts with the far more commonly and consistently cited rule.
DIG_BALA_STRONGEST_HOUSE = {
    Graha.JUPITER: 1, Graha.MERCURY: 1,
    Graha.SUN: 10, Graha.MARS: 10,
    Graha.VENUS: 4, Graha.MOON: 4,
    Graha.SATURN: 7,
}


def _angular_distance_0_180(a: float, b: float) -> float:
    """Shortest angular distance between two longitudes, folded to 0-180
    -- the same 'if over 180, subtract from 360' pattern used throughout
    classical Shadbala formulas (uchcha bala, dig bala alike)."""
    diff = abs(norm360(a) - norm360(b))
    return 360 - diff if diff > 180 else diff


def uchcha_bala(planet: Graha, sidereal_longitude: float) -> float:
    """
    Exaltation strength, 0-60 Virupas. Formula (BPHS 27.1, cross-checked
    against 4 independent sources including 2 worked numeric examples):
    distance from the DEBILITATION point (folded to 0-180) divided by 3.
    """
    exalt_sign, exalt_deg = EXALTATION_POINT[planet]
    debil_longitude = norm360(exalt_sign * 30 + exalt_deg + 180)
    distance = _angular_distance_0_180(sidereal_longitude, debil_longitude)
    return distance / 3.0


def ojayugmarasyamsa_bala(planet: Graha, rashi_longitude: float, navamsha_sign: int) -> float:
    """
    Odd/even sign strength, 0-30 Virupas (15 for Rashi + 15 for
    Navamsha). Male planets (Sun, Mars, Jupiter) and neutral planets
    (Mercury, Saturn) score in ODD signs; female planets (Moon, Venus)
    score in EVEN signs. Source: saravali.github.io (reference-
    implementation-grade documentation).
    """
    if planet not in MALE_PLANETS and planet not in FEMALE_PLANETS and planet not in NEUTRAL_PLANETS:
        return 0.0  # Rahu/Ketu not covered by this classical bala
    wants_odd = planet in MALE_PLANETS or planet in NEUTRAL_PLANETS

    rashi_sign = sign_index(rashi_longitude)
    rashi_is_odd = (rashi_sign % 2 == 0)  # Aries(0) is the 1st sign = odd
    navamsha_is_odd = (navamsha_sign % 2 == 0)

    score = 0.0
    if rashi_is_odd == wants_odd:
        score += 15.0
    if navamsha_is_odd == wants_odd:
        score += 15.0
    return score


def kendradi_bala(house_from_ascendant: int) -> float:
    """
    Angular strength, one of {60, 30, 15} Virupas. Kendra (1,4,7,10) =
    full strength; Panapara/succedent (2,5,8,11) = half; Apoklima/cadent
    (3,6,9,12) = quarter. Source: saravali.github.io.
    """
    if house_from_ascendant in (1, 4, 7, 10):
        return 60.0
    elif house_from_ascendant in (2, 5, 8, 11):
        return 30.0
    else:
        return 15.0


def drekkana_bala(planet: Graha, degree_in_sign_value: float) -> float:
    """
    Decanate strength, 0 or 15 Virupas. Male planets score in the 1st
    decanate (0-10 deg), female planets in the 2nd (10-20 deg), neutral
    planets in the 3rd (20-30 deg) -- for EVERY sign, no odd/even
    distinction (unlike D3 Drekkana varga, which this is NOT the same
    calculation as). Source: saravali.github.io.
    """
    decanate = min(int(degree_in_sign_value // 10), 2)  # 0, 1, or 2
    if planet in MALE_PLANETS and decanate == 0:
        return 15.0
    if planet in FEMALE_PLANETS and decanate == 1:
        return 15.0
    if planet in NEUTRAL_PLANETS and decanate == 2:
        return 15.0
    return 0.0


def dig_bala(planet: Graha, sidereal_longitude: float, ascendant: float, midheaven: float) -> float:
    """
    Directional strength, 0-60 Virupas. Full strength at the planet's
    preferred angle, falling linearly to zero at the diametrically
    opposite angle. Uses the actual Ascendant/Midheaven degrees (not
    whole-sign house boundaries) for precision.
    """
    if planet not in DIG_BALA_STRONGEST_HOUSE:
        return 0.0  # Rahu/Ketu not covered by classical Dig Bala
    strongest_house = DIG_BALA_STRONGEST_HOUSE[planet]

    # Map house number to its actual cusp longitude for this chart.
    house_points = {1: ascendant, 10: midheaven,
                    7: norm360(ascendant + 180), 4: norm360(midheaven + 180)}
    strongest_point = house_points[strongest_house]
    weakest_point = norm360(strongest_point + 180)

    distance_from_weakest = _angular_distance_0_180(sidereal_longitude, weakest_point)
    return (distance_from_weakest / 180.0) * 60.0


def naisargika_bala(planet: Graha) -> float:
    return NAISARGIKA_BALA.get(planet, 0.0)


def sthana_bala(planet: Graha, sidereal_longitude: float, navamsha_sign: int,
                 house_from_ascendant: int, natal_positions: dict) -> dict:
    """
    Full Sthana Bala: all 5 classical sub-components, including
    Saptavargaja Bala (see saptavargaja.py for its sourcing). The
    'total' key is now a genuine total, not a partial one -- comparable
    to classical Sthana Bala thresholds (max 390 Virupas).

    natal_positions: {Graha: sidereal_longitude} for all 7 classical
    grahas -- required by Saptavargaja Bala's temporary-friendship
    calculation, which needs to know where every planet is, not just
    the one being scored.
    """
    if planet not in EXALTATION_POINT:
        return {"note": "Uchcha/dignity-based balas are not defined for Rahu/Ketu in this module."}

    deg = degree_in_sign(sidereal_longitude)
    saptavargaja_result = saptavargaja_mod.saptavargaja_bala(planet, natal_positions)
    components = {
        "uchcha_bala": round(uchcha_bala(planet, sidereal_longitude), 3),
        "ojayugmarasyamsa_bala": round(ojayugmarasyamsa_bala(planet, sidereal_longitude, navamsha_sign), 3),
        "kendradi_bala": kendradi_bala(house_from_ascendant),
        "drekkana_bala": drekkana_bala(planet, deg),
        "saptavargaja_bala": saptavargaja_result.get("total"),
        "saptavargaja_breakdown": saptavargaja_result,
    }
    total = sum(v for k, v in components.items()
                if k not in ("saptavargaja_breakdown",) and v is not None)
    components["total"] = round(total, 3)
    return components


def kala_bala_partial(planet: Graha, birth_dt: datetime, utc_offset_hours: float,
                       latitude: float, longitude: float,
                       sun_tropical: float, moon_tropical: float,
                       planet_tropical_longitude: float, ayanamsa) -> dict:
    """
    Sum of the 5 IMPLEMENTED Kala Bala sub-components (Nathonnata,
    Paksha, Tribhaga, Ayana, Varsha+Masa+Dina+Hora) -- see kalabala.py
    for sourcing. Explicitly excludes Yuddha Bala; 'total' here is a
    partial total, not comparable to full Kala Bala thresholds.

    Note: Ayana Bala needs the planet's TROPICAL longitude specifically
    (declination is inherently a tropical-frame quantity) -- pass that,
    not the sidereal longitude used everywhere else in this package.
    """
    is_day, period_start, period_end = kalabala_mod.resolve_day_night_period(
        birth_dt, utc_offset_hours, latitude, longitude)
    third = kalabala_mod.tribhaga_third_from_time(birth_dt, period_start, period_end, is_day)
    vmdh = kalabala_mod.varsha_masa_dina_hora_bala(
        planet, birth_dt, utc_offset_hours, latitude, longitude, ayanamsa)

    components = {
        "nathonnata_bala": round(kalabala_mod.nathonnata_bala(planet, birth_dt), 3),
        "paksha_bala": round(kalabala_mod.paksha_bala(planet, moon_tropical, sun_tropical), 3),
        "tribhaga_bala": kalabala_mod.tribhaga_bala(planet, *third),
        "ayana_bala": round(kalabala_mod.ayana_bala(planet, planet_tropical_longitude), 3),
        "varsha_masa_dina_hora_bala": vmdh["total"],
    }
    components["varsha_masa_dina_hora_breakdown"] = vmdh
    components["total"] = round(sum(v for k, v in components.items()
                                     if k != "varsha_masa_dina_hora_breakdown"), 3)
    components["note"] = ("Excludes Yuddha Bala (not implemented) -- "
                           "not comparable to classical Kala Bala thresholds.")
    return components


def chesta_bala_partial(planet: Graha, kala_bala_components: dict, epoch=None,
                         planet_true_tropical_longitude: float = None):
    """
    Chesta Bala for all 7 classical grahas. Sun and Moon use BPHS's
    explicit substitution rule (their Ayana/Paksha Bala value, already
    in kala_bala_components). The other 5 use the actual motion-based
    formula (kalabala.chesta_bala_non_luminary) -- pass `epoch` and
    `planet_true_tropical_longitude` for those. Returns None only for
    Rahu/Ketu, which this classical bala doesn't cover.
    """
    if planet == Graha.SUN:
        return kala_bala_components["ayana_bala"]
    if planet == Graha.MOON:
        return kala_bala_components["paksha_bala"]
    if planet in (Graha.MARS, Graha.MERCURY, Graha.JUPITER, Graha.VENUS, Graha.SATURN):
        if epoch is None or planet_true_tropical_longitude is None:
            return None  # caller didn't supply what's needed -- explicit None, not a guess
        return round(kalabala_mod.chesta_bala_non_luminary(planet, epoch, planet_true_tropical_longitude), 3)
    return None  # Rahu/Ketu -- not covered by this classical bala


def shadbala_report(planet: Graha, sidereal_longitude: float, navamsha_sign: int,
                     house_from_ascendant: int, ascendant: float, midheaven: float,
                     natal_positions: dict, tropical_positions: dict,
                     birth_dt: datetime, utc_offset_hours: float,
                     latitude: float, longitude: float, ayanamsa, birth_epoch=None,
                     moon_is_waxing: bool = True) -> dict:
    """
    Full Shadbala report for one planet: Sthana Bala (all 5
    sub-components), Dig Bala, Naisargika Bala, Kala Bala, Chesta Bala,
    and Drik Bala. NOTE: Yuddha Bala (part of Kala Bala) requires
    comparing TWO planets' Tri-bala head to head and so cannot be
    resolved from a single planet in isolation -- use
    full_shadbala_for_chart() for a mutually-consistent set that
    includes it. This function's kala_bala total omits any Yuddha
    adjustment even if `planet` is currently at war.

    birth_epoch: a pymeeus Epoch for the birth moment, needed by Chesta
    Bala's non-luminary formula (orbital-element mean longitude lookups
    are keyed by Epoch). If omitted, Chesta Bala for the 5 non-luminary
    planets falls back to None rather than guessing.

    tropical_positions: {Graha: tropical_longitude} for at least Sun,
    Moon, and `planet` itself -- needed by Kala Bala's Ayana/Paksha/
    Nathonnata sub-formulas, which are inherently tropical-frame
    calculations (ayanamsa cancels out for Paksha/Nathonnata since
    they're relative, but Ayana Bala's declination is not ayanamsa-
    independent, so the TRUE tropical longitude is required).

    natal_positions: also used for Drik Bala (the aspect-angle
    difference is ayanamsa-independent, so sidereal positions work
    fine here).
    """
    sthana = sthana_bala(planet, sidereal_longitude, navamsha_sign, house_from_ascendant, natal_positions)
    dig = dig_bala(planet, sidereal_longitude, ascendant, midheaven)
    naisargika = naisargika_bala(planet)
    kala = kala_bala_partial(
        planet, birth_dt, utc_offset_hours, latitude, longitude,
        sun_tropical=tropical_positions[Graha.SUN],
        moon_tropical=tropical_positions[Graha.MOON],
        planet_tropical_longitude=tropical_positions[planet],
        ayanamsa=ayanamsa,
    )
    chesta = chesta_bala_partial(planet, kala, epoch=birth_epoch,
                                  planet_true_tropical_longitude=tropical_positions.get(planet))
    drik = drikbala_mod.drik_bala(planet, natal_positions, moon_is_waxing=moon_is_waxing)

    implemented_values = []
    if "total" in sthana:
        implemented_values.append(sthana["total"])
    implemented_values += [dig, naisargika, kala["total"], drik["total"]]
    if chesta is not None:
        implemented_values.append(chesta)

    missing = ["yuddha_bala (needs full_shadbala_for_chart)"]
    if chesta is None:
        missing.insert(0, "chesta_bala")
    return {
        "sthana_bala": sthana,
        "dig_bala": round(dig, 3),
        "kala_bala": kala,
        "chesta_bala": chesta,
        "naisargika_bala": naisargika,
        "drik_bala": drik,
        "partial_total_virupas": round(sum(implemented_values), 3),
        "missing_components": missing,
        "warning": "Total omits Yuddha Bala -- use full_shadbala_for_chart() for a war-adjusted total.",
    }


def full_shadbala_for_chart(natal_positions: dict, tropical_positions: dict,
                             ascendant: float, midheaven: float,
                             birth_dt: datetime, utc_offset_hours: float,
                             latitude: float, longitude: float, ayanamsa,
                             birth_epoch, navamsha_signs: dict, houses_from_ascendant: dict,
                             moon_is_waxing: bool = True) -> dict:
    """
    Shadbala for ALL 7 classical grahas at once, with Yuddha Bala
    correctly resolved and applied -- the only entry point that gives a
    complete, mutually-consistent Shadbala set. Use this rather than
    calling shadbala_report() once per planet if Yuddha Bala matters to
    you (it usually only affects a chart when two Tara Graha happen to
    sit within 1 degree of each other, which is uncommon but real).

    navamsha_signs / houses_from_ascendant: {Graha: value} pre-computed
    by the caller (chart.py already has this logic) -- kept as plain
    dicts here rather than recomputing varga/house placement inside this
    module, to avoid a circular import on varga.py.
    """
    classical = [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                 Graha.JUPITER, Graha.VENUS, Graha.SATURN]

    reports = {}
    for planet in classical:
        reports[planet] = shadbala_report(
            planet, natal_positions[planet], navamsha_signs[planet],
            houses_from_ascendant[planet], ascendant, midheaven,
            natal_positions, tropical_positions, birth_dt, utc_offset_hours,
            latitude, longitude, ayanamsa, birth_epoch=birth_epoch,
            moon_is_waxing=moon_is_waxing,
        )

    wars = yuddhabala_mod.find_all_wars(tropical_positions)
    for planet_a, planet_b in wars:
        tribala_a = reports[planet_a]["sthana_bala"].get("total", 0) + \
            reports[planet_a]["dig_bala"] + \
            (reports[planet_a]["kala_bala"]["total"] - reports[planet_a]["kala_bala"]["ayana_bala"])
        tribala_b = reports[planet_b]["sthana_bala"].get("total", 0) + \
            reports[planet_b]["dig_bala"] + \
            (reports[planet_b]["kala_bala"]["total"] - reports[planet_b]["kala_bala"]["ayana_bala"])

        resolution = yuddhabala_mod.yuddha_bala_adjustment(
            planet_a, tropical_positions[planet_a], tribala_a,
            planet_b, tropical_positions[planet_b], tribala_b,
        )
        winner, loser, adjustment = resolution["winner"], resolution["loser"], resolution["adjustment"]

        reports[winner]["kala_bala"]["yuddha_bala_adjustment"] = adjustment
        reports[winner]["kala_bala"]["total"] = round(reports[winner]["kala_bala"]["total"] + adjustment, 3)
        reports[loser]["kala_bala"]["yuddha_bala_adjustment"] = -adjustment
        reports[loser]["kala_bala"]["total"] = round(reports[loser]["kala_bala"]["total"] - adjustment, 3)

        for p in (winner, loser):
            reports[p]["missing_components"] = [m for m in reports[p]["missing_components"]
                                                 if not m.startswith("yuddha_bala")]
            reports[p]["partial_total_virupas"] = round(
                reports[p]["partial_total_virupas"] +
                (adjustment if p == winner else -adjustment), 3)
            reports[p]["warning"] = "Complete Shadbala total, including Yuddha Bala."

    return reports