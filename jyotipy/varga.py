"""
Divisional (Varga) charts: each maps a sidereal longitude to a *varga
sign* based on classical Parashari division rules (Brihat Parashara Hora
Shastra). A varga chart's "planet position" is just a sign (0-11) --
there's no sub-degree position within a varga, by definition.

HONESTY NOTE: the full classical Shodashavarga (16 divisional charts) has
rules for D16 through D60 that vary between source texts and are easy to
transcribe wrong from memory in ways that silently corrupt every reading
built on them. Rather than ship six divisional charts I'm not fully
confident are correct, this module implements the 8 vargas whose rules
are unambiguous and consistently documented across sources (D1-D12), and
raises NotImplementedError with an explanation for the rest. Fill those
in against a primary source (BPHS translation, or cross-check with an
established tool) before relying on them -- see README roadmap.
"""

from .constants import SIGNS
from .utils import sign_index as tropical_sign_index, degree_in_sign

MOVABLE = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
FIXED = {1, 4, 7, 10}    # Taurus, Leo, Scorpio, Aquarius
DUAL = {2, 5, 8, 11}     # Gemini, Virgo, Sagittarius, Pisces


def _sign_and_deg(sidereal_longitude: float):
    return tropical_sign_index(sidereal_longitude), degree_in_sign(sidereal_longitude)


def d1_rashi(sidereal_longitude: float) -> int:
    """Birth chart itself -- identity mapping."""
    s, _ = _sign_and_deg(sidereal_longitude)
    return s


def d2_hora(sidereal_longitude: float) -> int:
    """Hora: 2 parts of 15 deg. Parashari Sun/Moon hora scheme."""
    s, d = _sign_and_deg(sidereal_longitude)
    half = 0 if d < 15 else 1
    is_odd_sign = (s % 2 == 0)  # Aries(0)=1st sign=odd
    if is_odd_sign:
        return 4 if half == 0 else 3   # Leo (Sun) then Cancer (Moon)
    else:
        return 3 if half == 0 else 4   # Cancer then Leo


def d3_drekkana(sidereal_longitude: float) -> int:
    """Drekkana: 3 parts of 10 deg, trine (1-5-9) scheme."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = int(d // 10)  # 0, 1, 2
    return (s + part * 4) % 12


def d4_chaturthamsha(sidereal_longitude: float) -> int:
    """Chaturthamsha: 4 parts of 7d30', kendra (1-4-7-10) scheme."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = int(d // 7.5)  # 0..3
    return (s + part * 3) % 12


def d7_saptamsha(sidereal_longitude: float) -> int:
    """Saptamsha: 7 parts of ~4d17'8.57". Odd signs start from same sign,
    even signs start from the 7th sign therefrom."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = int(d // (30.0 / 7.0))  # 0..6
    is_odd_sign = (s % 2 == 0)
    start = s if is_odd_sign else (s + 6) % 12
    return (start + part) % 12


def d9_navamsha(sidereal_longitude: float) -> int:
    """Navamsha: 9 parts of 3d20'. Starting sign depends on the modality
    (movable/fixed/dual) of the birth sign."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = int(d // (10.0 / 3.0))  # 0..8
    if s in MOVABLE:
        start = s
    elif s in FIXED:
        start = (s + 8) % 12   # 9th sign from it
    else:  # DUAL
        start = (s + 4) % 12   # 5th sign from it
    return (start + part) % 12


def d10_dashamsha(sidereal_longitude: float) -> int:
    """Dashamsha: 10 parts of 3 deg. Odd signs start from same sign,
    even signs start from the 9th sign therefrom."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = int(d // 3.0)  # 0..9
    is_odd_sign = (s % 2 == 0)
    start = s if is_odd_sign else (s + 8) % 12
    return (start + part) % 12


def d12_dwadashamsha(sidereal_longitude: float) -> int:
    """Dwadashamsha: 12 parts of 2d30', always counted from the same sign."""
    s, d = _sign_and_deg(sidereal_longitude)
    part = int(d // 2.5)  # 0..11
    return (s + part) % 12


def _not_implemented(name):
    def _fn(sidereal_longitude: float) -> int:
        raise NotImplementedError(
            f"{name} is not implemented yet -- its classical starting-sign "
            f"rule needs verification against a primary source before "
            f"shipping (see varga.py module docstring / README roadmap)."
        )
    return _fn


d16_shodashamsha = _not_implemented("D16 Shodashamsha")
d20_vimshamsha = _not_implemented("D20 Vimshamsha")
d24_chaturvimshamsha = _not_implemented("D24 Chaturvimshamsha")
d27_nakshatramsha = _not_implemented("D27 Saptavimshamsha")
d30_trimshamsha = _not_implemented("D30 Trimshamsha")
d40_khavedamsha = _not_implemented("D40 Khavedamsha")
d45_akshavedamsha = _not_implemented("D45 Akshavedamsha")
d60_shashtiamsha = _not_implemented("D60 Shashtiamsha")

VARGA_FUNCTIONS = {
    "D1": d1_rashi, "D2": d2_hora, "D3": d3_drekkana, "D4": d4_chaturthamsha,
    "D7": d7_saptamsha, "D9": d9_navamsha, "D10": d10_dashamsha,
    "D12": d12_dwadashamsha,
    "D16": d16_shodashamsha, "D20": d20_vimshamsha,
    "D24": d24_chaturvimshamsha, "D27": d27_nakshatramsha,
    "D30": d30_trimshamsha, "D40": d40_khavedamsha,
    "D45": d45_akshavedamsha, "D60": d60_shashtiamsha,
}

IMPLEMENTED_VARGAS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12"]


def varga_sign(sidereal_longitude: float, varga: str) -> int:
    """Return the 0-11 varga sign index for a sidereal longitude in the
    given divisional chart (e.g. varga="D9")."""
    return VARGA_FUNCTIONS[varga](sidereal_longitude)


def varga_sign_name(sidereal_longitude: float, varga: str) -> str:
    return SIGNS[varga_sign(sidereal_longitude, varga)]
