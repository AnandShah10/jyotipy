"""
Yuddha Bala (planetary war): a correction applied to Kala Bala when two
"Tara Graha" (Mars, Mercury, Jupiter, Venus, Saturn -- NOT Sun, Moon,
Rahu, Ketu) come within 1 degree of each other.

SOURCING: cross-confirmed by 4 independent sources on the core mechanics
(a direct BPHS 27.20 quote via Medium/Varaha Mihira, a detailed slide
deck by the same author with a worked victor-determination diagram, a
dirah.org walkthrough, and a dineshcheramastro.com article) -- all
agreeing on: the 1-degree threshold, which 5 planets participate, that
the victor's more-northern declination wins, and the magnitude formula
(difference in Tri-bala [Sthana+Dig+Kala, EXCLUDING Ayana Bala] divided
by difference in angular disc diameter). The "exclude Ayana Bala"
detail specifically is confirmed by TWO independent sources
(dineshcheramastro AND the Varaha Mihira slide deck), not just one.

Disc diameters (Bimba Parimana) are attributed by name to a specific
published source (Dr. B.V. Raman's "Graha & Bhava Balas") by two
independent citing sources, giving this a real citation trail rather
than an anonymous number:
    Mars: 9.4", Mercury: 6.6", Jupiter: 190.4", Venus: 16.6", Saturn: 158.0"

VICTOR RULE: "the planet with more northern declination wins" (direct
BPHS quote). A second source expresses the identical rule differently
(higher tropical longitude wins during Uttarayana sign-range, lower
longitude wins during Dakshinayana) -- these are mathematically
equivalent, and cross-checking them against each other during
development confirmed they agree. This implementation uses declination
directly (already computed elsewhere in this package for Ayana Bala)
rather than the longitude-based equivalent, since it's the more direct
statement of the same rule.

ONE EXCEPTION found in the wider literature but NOT implemented here:
some sources (Ernst Wilhelm's article, Surya Siddhanta) claim Venus
always wins regardless of declination, and describe a further
"brightness order" tiebreaker. This is a real refinement beyond the
base BPHS rule, but was only found in secondary/tertiary sources
without the same direct-BPHS-quote backing as the core north-wins rule,
so it's noted here rather than silently included.
"""

from .constants import Graha
from .utils import norm360
from .kalabala import declination

TARA_GRAHA = {Graha.MARS, Graha.MERCURY, Graha.JUPITER, Graha.VENUS, Graha.SATURN}

# Bimba Parimana (angular disc diameter in arcseconds), per Dr. B.V.
# Raman's "Graha & Bhava Balas", cited by 2 independent sources.
DISC_DIAMETER_ARCSEC = {
    Graha.MARS: 9.4, Graha.MERCURY: 6.6, Graha.JUPITER: 190.4,
    Graha.VENUS: 16.6, Graha.SATURN: 158.0,
}

WAR_THRESHOLD_DEGREES = 1.0


def _angular_separation(lon_a: float, lon_b: float) -> float:
    diff = abs(norm360(lon_a) - norm360(lon_b))
    return 360.0 - diff if diff > 180.0 else diff


def is_planetary_war(planet_a: Graha, lon_a: float, planet_b: Graha, lon_b: float) -> bool:
    """True if both planets are Tara Graha and within 1 deg of each other."""
    if planet_a not in TARA_GRAHA or planet_b not in TARA_GRAHA:
        return False
    return _angular_separation(lon_a, lon_b) < WAR_THRESHOLD_DEGREES


def determine_victor(planet_a: Graha, tropical_lon_a: float,
                      planet_b: Graha, tropical_lon_b: float) -> Graha:
    """The planet with more northern declination wins (direct BPHS rule).
    Requires TROPICAL longitude (declination is a tropical-frame quantity)."""
    dec_a = declination(tropical_lon_a)
    dec_b = declination(tropical_lon_b)
    return planet_a if dec_a >= dec_b else planet_b


def yuddha_bala_magnitude(planet_a: Graha, tribala_a: float,
                           planet_b: Graha, tribala_b: float) -> float:
    """
    The Virupa amount transferred from loser to victor:
    |difference in Tri-bala| / |difference in disc diameter|.

    tribala_a/b: each planet's Sthana Bala + Dig Bala + Kala Bala
    (Kala Bala here EXCLUDING Ayana Bala, per the two-source-confirmed
    exclusion rule -- pass that pre-computed sum in, not full Kala Bala).
    """
    diameter_diff = abs(DISC_DIAMETER_ARCSEC[planet_a] - DISC_DIAMETER_ARCSEC[planet_b])
    if diameter_diff == 0:
        return 0.0  # guard against identical diameters (shouldn't occur among these 5)
    return abs(tribala_a - tribala_b) / diameter_diff


def yuddha_bala_adjustment(planet_a: Graha, tropical_lon_a: float, tribala_a: float,
                            planet_b: Graha, tropical_lon_b: float, tribala_b: float) -> dict:
    """
    Full Yuddha Bala resolution for a detected war between planet_a and
    planet_b. Returns {winner, loser, adjustment} -- `adjustment` (a
    positive Virupa amount) should be ADDED to the winner's Kala Bala
    and SUBTRACTED from the loser's.
    """
    winner = determine_victor(planet_a, tropical_lon_a, planet_b, tropical_lon_b)
    loser = planet_b if winner == planet_a else planet_a
    adjustment = yuddha_bala_magnitude(planet_a, tribala_a, planet_b, tribala_b)
    return {"winner": winner, "loser": loser, "adjustment": round(adjustment, 3)}


def find_all_wars(tropical_positions: dict) -> list:
    """Scan all pairs of Tara Graha in `tropical_positions` and return a
    list of (planet_a, planet_b) pairs currently at war."""
    wars = []
    tara_planets = [p for p in tropical_positions if p in TARA_GRAHA]
    for i, p1 in enumerate(tara_planets):
        for p2 in tara_planets[i + 1:]:
            if is_planetary_war(p1, tropical_positions[p1], p2, tropical_positions[p2]):
                wars.append((p1, p2))
    return wars