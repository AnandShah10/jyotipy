"""
Divisional (Varga) charts: each maps a sidereal longitude to a *varga
sign* based on classical Parashari division rules (Brihat Parashara Hora
Shastra). A varga chart's "planet position" is just a sign (0-11) --
there's no sub-degree position within a varga, by definition.

D1 through D12 use unambiguous rules cross-checked in v0.1. D16 through
D60 (added here) are each cross-checked against 2-3 independent published
sources for their starting-sign rule -- with ONE exception flagged below
(D60), where the sources themselves genuinely disagree, not just vary in
how they explain the same rule.
"""

from .constants import SIGNS, Graha
from .utils import sign_index as tropical_sign_index, degree_in_sign

MOVABLE = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
FIXED = {1, 4, 7, 10}    # Taurus, Leo, Scorpio, Aquarius
DUAL = {2, 5, 8, 11}     # Gemini, Virgo, Sagittarius, Pisces

FIRE = {0, 4, 8}         # Aries, Leo, Sagittarius
EARTH = {1, 5, 9}        # Taurus, Virgo, Capricorn
AIR = {2, 6, 10}         # Gemini, Libra, Aquarius
WATER = {3, 7, 11}       # Cancer, Scorpio, Pisces


def _sign_and_deg(sidereal_longitude: float):
    return tropical_sign_index(sidereal_longitude), degree_in_sign(sidereal_longitude)


def _modality_start(s: int, movable_start: int, fixed_start: int, dual_start: int) -> int:
    if s in MOVABLE:
        return movable_start
    elif s in FIXED:
        return fixed_start
    else:
        return dual_start


# -- D1 through D12 (unchanged from v0.1) -----------------------------

def d1_rashi(sidereal_longitude: float) -> int:
    """Birth chart itself -- identity mapping."""
    s, _ = _sign_and_deg(sidereal_longitude)
    return s


def d2_hora(sidereal_longitude: float) -> int:
    """Hora: 2 parts of 15 deg. Parashari Sun/Moon hora scheme."""
    s, d = _sign_and_deg(sidereal_longitude)
    half = 0 if d < 15 else 1
    is_odd_sign = (s % 2 == 0)
    if is_odd_sign:
        return 4 if half == 0 else 3   # Leo (Sun) then Cancer (Moon)
    else:
        return 3 if half == 0 else 4   # Cancer then Leo


def d3_drekkana(sidereal_longitude: float) -> int:
    """Drekkana: 3 parts of 10 deg, trine (1-5-9) scheme."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 10), 2)
    return (s + part * 4) % 12


def d4_chaturthamsha(sidereal_longitude: float) -> int:
    """Chaturthamsha: 4 parts of 7d30', kendra (1-4-7-10) scheme."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 7.5), 3)
    return (s + part * 3) % 12


def d7_saptamsha(sidereal_longitude: float) -> int:
    """Saptamsha: 7 parts of ~4d17'8.57". Odd signs start from same sign,
    even signs start from the 7th sign therefrom."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // (30.0 / 7.0)), 6)
    is_odd_sign = (s % 2 == 0)
    start = s if is_odd_sign else (s + 6) % 12
    return (start + part) % 12


def d9_navamsha(sidereal_longitude: float) -> int:
    """Navamsha: 9 parts of 3d20'. Starting sign depends on modality."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // (10.0 / 3.0)), 8)
    start = _modality_start(s, movable_start=s, fixed_start=(s + 8) % 12, dual_start=(s + 4) % 12)
    return (start + part) % 12


def d10_dashamsha(sidereal_longitude: float) -> int:
    """Dashamsha: 10 parts of 3 deg. Odd signs start from same sign,
    even signs start from the 9th sign therefrom."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 3.0), 9)
    is_odd_sign = (s % 2 == 0)
    start = s if is_odd_sign else (s + 8) % 12
    return (start + part) % 12


def d12_dwadashamsha(sidereal_longitude: float) -> int:
    """Dwadashamsha: 12 parts of 2d30', always counted from the same sign."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 2.5), 11)
    return (s + part) % 12


# -- D16 through D60 (new) ---------------------------------------------

def d16_shodashamsha(sidereal_longitude: float) -> int:
    """
    Shodashamsha (Kalamsha): 16 parts of 1d52'30". Movable signs start
    counting from Aries, fixed signs from Leo, dual signs from Sagittarius.
    Cross-checked against 3 independent sources (BPHS-attributed, all
    agree): indianastrologyarticles.blogspot.com, Grokipedia's Shodasamsa
    entry, and shreekundli.com's D16 guide.
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 1.875), 15)
    start = _modality_start(s, movable_start=0, fixed_start=4, dual_start=8)
    return (start + part) % 12


def d20_vimshamsha(sidereal_longitude: float) -> int:
    """
    Vimshamsha: 20 parts of 1d30'. Movable signs start from Aries, fixed
    signs from Sagittarius, dual signs from Leo -- note this rotation is
    NOT the same order as D16 (fixed/dual are swapped). Cross-checked
    against 2 independent sources (indianastrologyarticles.blogspot.com,
    vedastrology.blogspot.com), both agreeing on this exact rotation.
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 1.5), 19)
    start = _modality_start(s, movable_start=0, fixed_start=8, dual_start=4)
    return (start + part) % 12


def d24_chaturvimshamsha(sidereal_longitude: float) -> int:
    """
    Chaturvimshamsha (Siddhamsha): 24 parts of 1d15'. Odd signs start
    counting from Leo, even signs from Cancer, cyclic. Cross-checked
    against 2 independent sources (indianastrologyarticles.blogspot.com,
    Kambhampati's Astrological Works), both agreeing.
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 1.25), 23)
    is_odd_sign = (s % 2 == 0)
    start = 4 if is_odd_sign else 3   # Leo : Cancer
    return (start + part) % 12


def d27_nakshatramsha(sidereal_longitude: float) -> int:
    """
    Saptavimshamsha (Bhamsha/Nakshatramsha): 27 parts of 1d6'40". Starting
    sign depends on the birth sign's element (triplicity): fire signs
    start from Aries, earth from Cancer, air from Libra, water from
    Capricorn. Cross-checked against 2 independent sources
    (indianastrologyarticles.blogspot.com, Kambhampati's Astrological
    Works), both agreeing.
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // (30.0 / 27.0)), 26)
    if s in FIRE:
        start = 0
    elif s in EARTH:
        start = 3
    elif s in AIR:
        start = 6
    else:  # WATER
        start = 9
    return (start + part) % 12


# Trimshamsha (D30) planet-lord degree ranges, per the classical unequal
# division. Odd-sign order: Mars(0-5), Saturn(5-10), Jupiter(10-18),
# Mercury(18-25), Venus(25-30). Even-sign order is the exact reverse:
# Venus(0-5), Mercury(5-12), Jupiter(12-20), Saturn(20-25), Mars(25-30).
# Cross-checked against 4 independent sources (pinpointastrology.com,
# astrosight.ai, anandamoyee blog with a worked example, and
# srath.com/Sanjay Rath's site with a second independent worked example)
# -- all agreeing on both the degree ranges and the resulting sign
# assignment logic below.
_D30_ODD_RANGES = [
    (5, Graha.MARS), (10, Graha.SATURN), (18, Graha.JUPITER),
    (25, Graha.MERCURY), (30, Graha.VENUS),
]
_D30_EVEN_RANGES = [
    (5, Graha.VENUS), (12, Graha.MERCURY), (20, Graha.JUPITER),
    (25, Graha.SATURN), (30, Graha.MARS),
]
# Each of the 5 D30 lords owns one odd sign and one even sign (their two
# classical own-signs); the D30 result sign is THAT owned sign matching
# the birth sign's odd/even parity, not the birth sign itself.
_D30_LORD_OWN_SIGN = {
    Graha.MARS: {"odd": 0, "even": 7},        # Aries / Scorpio
    Graha.SATURN: {"odd": 10, "even": 9},     # Aquarius / Capricorn
    Graha.JUPITER: {"odd": 8, "even": 11},    # Sagittarius / Pisces
    Graha.MERCURY: {"odd": 2, "even": 5},     # Gemini / Virgo
    Graha.VENUS: {"odd": 6, "even": 1},       # Libra / Taurus
}


def d30_trimshamsha(sidereal_longitude: float) -> int:
    """Trimshamsha: unequal division ruled by the 5 non-luminous grahas
    (Sun, Moon, Rahu, Ketu never rule a trimshamsha portion). See module-
    level comment above for the sourcing on the degree ranges."""
    s, d = _sign_and_deg(sidereal_longitude)
    is_odd_sign = (s % 2 == 0)
    ranges = _D30_ODD_RANGES if is_odd_sign else _D30_EVEN_RANGES
    lord = ranges[-1][1]
    for boundary, graha in ranges:
        if d < boundary:
            lord = graha
            break
    parity = "odd" if is_odd_sign else "even"
    return _D30_LORD_OWN_SIGN[lord][parity]


def d40_khavedamsha(sidereal_longitude: float) -> int:
    """
    Khavedamsha (Chatvarimshamsha): 40 parts of 0d45'. Odd signs start
    counting from Aries, even signs from Libra. Cross-checked against 2
    independent sources (Kambhampati's Astrological Works and its
    wordpress mirror), agreeing.
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 0.75), 39)
    is_odd_sign = (s % 2 == 0)
    start = 0 if is_odd_sign else 6   # Aries : Libra
    return (start + part) % 12


def d45_akshavedamsha(sidereal_longitude: float) -> int:
    """
    Akshavedamsha: 45 parts of 0d40'. Movable signs start from Aries,
    fixed from Leo, dual from Sagittarius -- the same rotation as D16.
    Cross-checked against Kambhampati's Astrological Works (single
    strong source; corroborated only indirectly elsewhere, so slightly
    less independently verified than the other additions here -- treat
    with a bit more caution than D16/D20/D24/D27/D40 if this one matters
    to your specific use case).
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // (2.0 / 3.0)), 44)
    start = _modality_start(s, movable_start=0, fixed_start=4, dual_start=8)
    return (start + part) % 12


def d60_shashtiamsha(sidereal_longitude: float) -> int:
    """
    Shashtiamsha: 60 parts of 0d30'. UNRESOLVED DISCREPANCY IN THE
    SOURCES -- two genuinely different classical methods are in active
    use and disagree on the resulting sign:

      1. "JHora method" (what most modern software, including
         Jagannatha Hora, actually implements): find which of the 60
         parts the longitude falls into (part = floor(degree_in_sign /
         0.5) + 1, range 1-60), then count that many signs INCLUSIVELY
         starting from the planet's OWN birth sign. This is what's
         implemented below.

      2. "Literal BPHS text method" (per a forum thread of practitioners
         explicitly debating this discrepancy): ignore the birth sign
         entirely, multiply degree-in-sign by 2, divide by 12, and use
         the remainder+1 counted from Aries -- meaning two planets at
         the same degree-in-sign in DIFFERENT signs would land in the
         SAME D60 sign under this method, which method 1 would never
         produce.

    These are not two descriptions of the same rule -- they produce
    different charts. This implementation uses method 1 (JHora-style)
    because it's what you'll be cross-checking against in practice. If
    your source material specifically follows the literal-BPHS reading,
    this function's output will disagree with it -- see the module
    docstring pattern used elsewhere in this file for how seriously to
    take that.
    """
    s, d = _sign_and_deg(sidereal_longitude)
    part = min(int(d // 0.5) + 1, 60)  # 1-indexed, 1..60
    return (s + part - 1) % 12  # count `part` signs inclusively from s


VARGA_FUNCTIONS = {
    "D1": d1_rashi, "D2": d2_hora, "D3": d3_drekkana, "D4": d4_chaturthamsha,
    "D7": d7_saptamsha, "D9": d9_navamsha, "D10": d10_dashamsha,
    "D12": d12_dwadashamsha,
    "D16": d16_shodashamsha, "D20": d20_vimshamsha,
    "D24": d24_chaturvimshamsha, "D27": d27_nakshatramsha,
    "D30": d30_trimshamsha, "D40": d40_khavedamsha,
    "D45": d45_akshavedamsha, "D60": d60_shashtiamsha,
}

IMPLEMENTED_VARGAS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
                      "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]


def varga_sign(sidereal_longitude: float, varga: str) -> int:
    """Return the 0-11 varga sign index for a sidereal longitude in the
    given divisional chart (e.g. varga="D9")."""
    return VARGA_FUNCTIONS[varga](sidereal_longitude)


def varga_sign_name(sidereal_longitude: float, varga: str) -> str:
    return SIGNS[varga_sign(sidereal_longitude, varga)]
