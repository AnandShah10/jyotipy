"""
Static reference data for JyotiPy: signs, nakshatras, planets, dasha periods.

Nothing in this file does math — it's pure lookup tables. Keeping it
separate means every other module can import names instead of hardcoding
strings, so a typo in "Purvashadha" only has to be fixed once.
"""

from enum import Enum


class Graha(str, Enum):
    """The 9 Vedic grahas (Navagraha). Rahu/Ketu are shadow points, not
    physical bodies, computed from the Moon's orbital nodes."""
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"


# Order matters for dasha sequencing (Vimshottari dasha lord order).
VIMSHOTTARI_ORDER = [
    Graha.KETU, Graha.VENUS, Graha.SUN, Graha.MOON, Graha.MARS,
    Graha.RAHU, Graha.JUPITER, Graha.SATURN, Graha.MERCURY,
]

# Total = 120 years, the full Vimshottari cycle.
VIMSHOTTARI_YEARS = {
    Graha.KETU: 7, Graha.VENUS: 20, Graha.SUN: 6, Graha.MOON: 10,
    Graha.MARS: 7, Graha.RAHU: 18, Graha.JUPITER: 16, Graha.SATURN: 19,
    Graha.MERCURY: 17,
}
assert sum(VIMSHOTTARI_YEARS.values()) == 120

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = {
    "Aries": Graha.MARS, "Taurus": Graha.VENUS, "Gemini": Graha.MERCURY,
    "Cancer": Graha.MOON, "Leo": Graha.SUN, "Virgo": Graha.MERCURY,
    "Libra": Graha.VENUS, "Scorpio": Graha.MARS, "Sagittarius": Graha.JUPITER,
    "Capricorn": Graha.SATURN, "Aquarius": Graha.SATURN, "Pisces": Graha.JUPITER,
}

# 27 nakshatras, each spanning exactly 13°20' (800') of the zodiac.
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Nakshatra lord cycle repeats the Vimshottari order 3x across 27 nakshatras.
NAKSHATRA_LORDS = [VIMSHOTTARI_ORDER[i % 9] for i in range(27)]

# Standard 16-varga (Shodasavarga) divisional chart divisors.
VARGA_DIVISIONS = {
    "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, "D10": 10,
    "D12": 12, "D16": 16, "D20": 20, "D24": 24, "D27": 27, "D30": 30,
    "D40": 40, "D45": 45, "D60": 60,
}

DEG_PER_SIGN = 30.0
DEG_PER_NAKSHATRA = 360.0 / 27.0  # 13.333...
DEG_PER_PADA = DEG_PER_NAKSHATRA / 4.0  # 3.333...
