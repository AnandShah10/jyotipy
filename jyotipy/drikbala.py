"""
Drik Bala (aspectual strength): the net effect of every other classical
graha's aspect on a given planet.

SOURCING: this was the hardest-won piece in the whole project. Multiple
sources describe the STRUCTURE (benefic aspects add, malefic aspects
subtract, Mercury and Jupiter's aspects are always fully added) but call
the underlying continuous formula "complicated"/"cumbersome" without
giving it. The actual formula was eventually found in a slide deck
("Shadbala: Concept and Computation") that includes both a textual
formula sketch AND a fully worked 30x12 reference grid -- reconstructing
the continuous formula from that grid and checking it against 5
independent points taken directly from the grid (including the deck's
own worked example: Jupiter aspecting the Sun from 192 deg away scores
+13.5) matched EXACTLY every time. That reconstructed formula, not a
guess, is what's implemented below:

    Drsti Kendra (DK) = aspected planet's longitude - aspecting
                         planet's longitude, normalized to 0-360

    DK in [0, 30)    -> 0
    DK in [30, 60)   -> (DK - 30) / 8
    DK in [60, 90)   -> (DK - 60) / 4 + 3.75
    DK in [90, 120)  -> (120 - DK) / 8 + 7.5
    DK in [120, 150) -> (150 - DK) / 4
    DK in [150, 180) -> (DK - 150) / 2      -- peaks at 15 at DK=180 (opposition/7th house)
    DK in [180, 300) -> (300 - DK) / 8
    DK in [300, 360) -> 0

This single continuous formula naturally reproduces the classical
special aspects (Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th) without
needing a separate override table -- e.g. it evaluates to 11.25 at
exactly 90 deg separation, matching the fixed reference value some
simplified summaries give for that same angle. Since the "Actual DrgBala
computation method" (this table) is explicitly distinguished in the
source from a separate, cruder "DrgBala Approximation" table, this
implementation uses the more precise continuous version throughout.

BENEFIC/MALEFIC SIGN: per the source's explicit classification --
Jupiter and Mercury are ALWAYS added in full ("super add the entire
Drishti of Budha and Guru" -- a direct BPHS 27.19 quote), Venus and a
waxing Moon are benefic (added), and Sun, Mars, Saturn, and a waning
Moon are malefic (subtracted). This is confirmed consistent with the
deck's own worked example, where Jupiter's aspect on the Sun is added
as a positive +13.5 with no further adjustment.
"""

from .constants import Graha
from .utils import norm360

MALEFICS = {Graha.SUN, Graha.MARS, Graha.SATURN}
ALWAYS_BENEFIC = {Graha.JUPITER, Graha.MERCURY}  # "super add the entire Drishti"
# Venus is benefic; Moon's sign depends on waxing/waning (passed in separately).


def drsti_bala_magnitude(drsti_kendra: float) -> float:
    """Raw (unsigned) aspect strength, 0-15 Virupas, from the Drsti
    Kendra -- see module docstring for the sourcing on this formula."""
    dk = norm360(drsti_kendra)
    if dk < 30:
        return 0.0
    elif dk < 60:
        return (dk - 30) / 8.0
    elif dk < 90:
        return (dk - 60) / 4.0 + 3.75
    elif dk < 120:
        return (120 - dk) / 8.0 + 7.5
    elif dk < 150:
        return (150 - dk) / 4.0
    elif dk < 180:
        return (dk - 150) / 2.0
    elif dk < 300:
        return (300 - dk) / 8.0
    else:
        return 0.0


def _is_benefic_contributor(aspecting_planet: Graha, moon_is_waxing: bool = True) -> bool:
    if aspecting_planet in ALWAYS_BENEFIC:
        return True
    if aspecting_planet == Graha.VENUS:
        return True
    if aspecting_planet == Graha.MOON:
        return moon_is_waxing
    return False  # Sun, Mars, Saturn


def drik_bala(target_planet: Graha, positions: dict, moon_is_waxing: bool = True) -> dict:
    """
    Full Drik Bala for `target_planet`: the signed sum of every other
    classical graha's aspect on it. Can be NEGATIVE -- a negative value
    is a real result (net malefic influence), not an error, and should
    never be clamped to zero.

    positions: {Graha: sidereal_or_tropical_longitude} for target_planet
    and every other classical graha aspecting it (ayanamsa cancels out
    in the DK difference, so either frame works as long as it's used
    consistently for all planets passed in).
    """
    target_lon = positions[target_planet]
    contributions = {}
    for aspecting_planet, aspecting_lon in positions.items():
        if aspecting_planet == target_planet:
            continue
        if aspecting_planet in (Graha.RAHU, Graha.KETU):
            continue  # not classical grahas for this purpose
        dk = target_lon - aspecting_lon
        magnitude = drsti_bala_magnitude(dk)
        is_benefic = _is_benefic_contributor(aspecting_planet, moon_is_waxing)
        signed = magnitude if is_benefic else -magnitude
        contributions[aspecting_planet.value] = round(signed, 3)

    total = sum(contributions.values())
    return {"contributions": contributions, "total": round(total, 3)}