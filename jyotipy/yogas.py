"""
Yoga detection: classical planetary combinations checked against a
computed chart. This module implements a deliberately conservative core
set -- yogas whose defining rule is unambiguous and consistently stated
across sources -- rather than the hundreds of yogas found across the
Jyotish corpus, many of which have text-dependent variant definitions.
Treat this as a foundation to extend, not a complete yoga encyclopedia.

Input to every function here is a `positions` dict of
{Graha: sidereal_longitude_degrees} plus the ascendant's sidereal
longitude, matching what chart.py produces.
"""

from .constants import Graha, SIGNS

EXALTATION_SIGN = {
    Graha.SUN: 0, Graha.MOON: 1, Graha.MARS: 9, Graha.MERCURY: 5,
    Graha.JUPITER: 3, Graha.VENUS: 11, Graha.SATURN: 6,
}
DEBILITATION_SIGN = {g: (s + 6) % 12 for g, s in EXALTATION_SIGN.items()}

OWN_SIGNS = {
    Graha.SUN: {4}, Graha.MOON: {3}, Graha.MARS: {0, 7},
    Graha.MERCURY: {2, 5}, Graha.JUPITER: {8, 11}, Graha.VENUS: {1, 6},
    Graha.SATURN: {9, 10},
}

PANCHA_MAHAPURUSHA = {
    Graha.MARS: "Ruchaka", Graha.MERCURY: "Bhadra", Graha.JUPITER: "Hamsa",
    Graha.VENUS: "Malavya", Graha.SATURN: "Sasa",
}

KENDRA_OFFSETS = {0, 3, 6, 9}  # houses 1,4,7,10 as sign-distance from a reference


def _sign(longitude: float) -> int:
    return int(longitude % 360 // 30)


def _sign_distance(from_sign: int, to_sign: int) -> int:
    """0-11 distance counting forward from from_sign to to_sign."""
    return (to_sign - from_sign) % 12


def detect_pancha_mahapurusha(positions: dict, ascendant_longitude: float) -> list:
    """Ruchaka/Bhadra/Hamsa/Malavya/Sasa: the karaka planet is in its own
    or exaltation sign AND in a kendra (1/4/7/10) from the ascendant."""
    found = []
    asc_sign = _sign(ascendant_longitude)
    for graha, name in PANCHA_MAHAPURUSHA.items():
        lon = positions[graha]
        s = _sign(lon)
        in_own_or_exalted = (s in OWN_SIGNS[graha]) or (s == EXALTATION_SIGN[graha])
        in_kendra = _sign_distance(asc_sign, s) in KENDRA_OFFSETS
        if in_own_or_exalted and in_kendra:
            found.append({"yoga": name, "graha": graha, "sign": SIGNS[s]})
    return found


def detect_gajakesari(positions: dict) -> bool:
    """Jupiter in a kendra (1/4/7/10) counted from the Moon."""
    moon_sign = _sign(positions[Graha.MOON])
    jup_sign = _sign(positions[Graha.JUPITER])
    return _sign_distance(moon_sign, jup_sign) in KENDRA_OFFSETS


def detect_budhaditya(positions: dict) -> bool:
    """Sun and Mercury conjunct (same sign)."""
    return _sign(positions[Graha.SUN]) == _sign(positions[Graha.MERCURY])


def detect_chandra_mangal(positions: dict) -> bool:
    """Moon and Mars conjunct (same sign) -- indicates wealth-generating
    drive when well-placed; classically also considered malefic in some
    contexts depending on house. This function only checks the raw
    combination, not house context."""
    return _sign(positions[Graha.MOON]) == _sign(positions[Graha.MARS])


def _planets_from_moon(positions: dict, sign_offset: int, exclude=(Graha.SUN, Graha.MOON)) -> list:
    moon_sign = _sign(positions[Graha.MOON])
    target_sign = (moon_sign + sign_offset) % 12
    return [g for g, lon in positions.items()
            if g not in exclude and _sign(lon) == target_sign]


def detect_sunapha_anapha_durudhara(positions: dict) -> dict:
    """
    Sunapha: any planet (except Sun) in the 2nd sign from the Moon.
    Anapha: any planet (except Sun) in the 12th sign from the Moon.
    Durudhara: both conditions hold simultaneously.
    If neither holds and the Moon itself isn't otherwise supported, that's
    the setup for Kemadruma (checked separately).
    """
    second = _planets_from_moon(positions, 1)
    twelfth = _planets_from_moon(positions, 11)
    result = {"sunapha": bool(second), "anapha": bool(twelfth),
              "durudhara": bool(second) and bool(twelfth),
              "planets_2nd_from_moon": second, "planets_12th_from_moon": twelfth}
    return result


def detect_kemadruma(positions: dict) -> bool:
    """
    Simplified Kemadruma: no planets (other than Sun) in the 1st, 2nd, or
    12th sign from the Moon. Classical texts also list several
    cancellation (bhanga) conditions -- e.g. planets in kendra from the
    ascendant -- which are NOT checked here. Treat a True result as "the
    raw combination is present," not a final verdict; always check
    cancellation conditions manually for this one.
    """
    same = _planets_from_moon(positions, 0)
    second = _planets_from_moon(positions, 1)
    twelfth = _planets_from_moon(positions, 11)
    return not (same or second or twelfth)


def detect_neechabhanga_candidates(positions: dict, ascendant_longitude: float) -> list:
    """
    Simplified Neecha Bhanga Raja Yoga check: for each debilitated graha,
    flags it as a *candidate* if the lord of its debilitation sign is
    itself in a kendra (1/4/7/10) from the ascendant or from the Moon.
    This is only the most commonly cited primary cancellation rule --
    classical texts list several independent cancellation conditions
    (mutual kendra placement, exchange, exaltation navamsha, etc.) that
    this function does not check. A True/candidate result means "worth
    investigating further," not "confirmed raja yoga."
    """
    from .constants import SIGN_LORDS, SIGNS as SIGN_NAMES
    asc_sign = _sign(ascendant_longitude)
    moon_sign = _sign(positions[Graha.MOON])
    candidates = []
    for graha, lon in positions.items():
        if graha in (Graha.RAHU, Graha.KETU):
            continue
        s = _sign(lon)
        if DEBILITATION_SIGN.get(graha) == s:
            debil_sign_name = SIGN_NAMES[s]
            dispositor = SIGN_LORDS[debil_sign_name]
            dispositor_sign = _sign(positions[dispositor])
            from_asc = _sign_distance(asc_sign, dispositor_sign) in KENDRA_OFFSETS
            from_moon = _sign_distance(moon_sign, dispositor_sign) in KENDRA_OFFSETS
            if from_asc or from_moon:
                candidates.append({
                    "graha": graha, "debilitated_in": debil_sign_name,
                    "dispositor": dispositor,
                    "cancellation_basis": "kendra_from_asc" if from_asc else "kendra_from_moon",
                })
    return candidates


def detect_all_yogas(positions: dict, ascendant_longitude: float) -> dict:
    """Run the full v0.1 yoga check set and return a structured report."""
    return {
        "pancha_mahapurusha": detect_pancha_mahapurusha(positions, ascendant_longitude),
        "gajakesari": detect_gajakesari(positions),
        "budhaditya": detect_budhaditya(positions),
        "chandra_mangal": detect_chandra_mangal(positions),
        "moon_strength": detect_sunapha_anapha_durudhara(positions),
        "kemadruma_raw": detect_kemadruma(positions),
        "neechabhanga_candidates": detect_neechabhanga_candidates(positions, ascendant_longitude),
    }
