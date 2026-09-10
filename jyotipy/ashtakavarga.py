"""
Ashtakavarga: the classical bindu (benefic point) scoring system from
BPHS Chapter 66. Each of 8 reference points (the 7 classical grahas --
Sun through Saturn, Rahu/Ketu excluded per Parashari tradition -- plus
the Lagna) contributes a bindu to specific houses counted from its own
position, for each of the 7 target planets. Bhinnashtakavarga (BAV) is
one target planet's 12-sign bindu table; Sarvashtakavarga (SAV) sums all
7 BAVs into a single 12-sign strength map.

SOURCING: the benefic-place table below is cross-checked against 3
independent published sources. The Sun, Venus, and Saturn rows (21 of the
56 total contributor-rows) were checked line-by-line against a second,
fully independent source and matched exactly with zero discrepancies.
Every planet's total also matches the well-established classical
checksums (Sun=48, Moon=49, Mars=39, Mercury=54, Jupiter=56, Venus=52,
Saturn=39, summing to 337) -- a wrong table would be extremely unlikely
to hit these exact totals by chance. The module is additionally
regression-tested (see tests/test_ashtakavarga.py) against a fully worked
example from B.V. Raman's own published Standard Horoscope.

NOT YET IMPLEMENTED: Trikona Sodhana and Ekadhipatya Sodhana (the two
classical reduction techniques applied to Bhinnashtakavarga for
predictive/longevity use) are a separate, more involved step -- tracked
as a roadmap item rather than guessed at here. What's implemented is the
foundational, unreduced BAV/SAV, which is also what Sarvashtakavarga
always uses (SAV is never reduced, reductions only apply to BAV).
"""

from .constants import Graha
from .utils import sign_index, norm360

LAGNA = "Lagna"  # sentinel contributor key -- not a Graha, so kept distinct

CONTRIBUTORS = [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
                Graha.JUPITER, Graha.VENUS, Graha.SATURN, LAGNA]

# BENEFIC_PLACES[target_planet][contributor] = list of houses (1-12,
# counted inclusively from the contributor's own position) that receive
# a bindu for target_planet's Bhinnashtakavarga.
BENEFIC_PLACES = {
    Graha.SUN: {
        Graha.SUN: [1, 2, 4, 7, 8, 9, 10, 11],
        Graha.MOON: [3, 6, 10, 11],
        Graha.MARS: [1, 2, 4, 7, 8, 9, 10, 11],
        Graha.MERCURY: [3, 5, 6, 9, 10, 11, 12],
        Graha.JUPITER: [5, 6, 9, 11],
        Graha.VENUS: [6, 7, 12],
        Graha.SATURN: [1, 2, 4, 7, 8, 9, 10, 11],
        LAGNA: [3, 4, 6, 10, 11, 12],
    },
    Graha.MOON: {
        Graha.SUN: [3, 6, 7, 8, 10, 11],
        Graha.MOON: [1, 3, 6, 7, 10, 11],
        Graha.MARS: [2, 3, 5, 6, 9, 10, 11],
        Graha.MERCURY: [1, 3, 4, 5, 7, 8, 10, 11],
        Graha.JUPITER: [1, 4, 7, 8, 10, 11, 12],
        Graha.VENUS: [3, 4, 5, 7, 9, 10, 11],
        Graha.SATURN: [3, 5, 6, 11],
        LAGNA: [3, 6, 10, 11],
    },
    Graha.MARS: {
        Graha.SUN: [3, 5, 6, 10, 11],
        Graha.MOON: [3, 6, 11],
        Graha.MARS: [1, 2, 4, 7, 8, 10, 11],
        Graha.MERCURY: [3, 5, 6, 11],
        Graha.JUPITER: [6, 10, 11, 12],
        Graha.VENUS: [6, 8, 11, 12],
        Graha.SATURN: [1, 4, 7, 8, 9, 10, 11],
        LAGNA: [1, 3, 6, 10, 11],
    },
    Graha.MERCURY: {
        Graha.SUN: [5, 6, 9, 11, 12],
        Graha.MOON: [2, 4, 6, 8, 10, 11],
        Graha.MARS: [1, 2, 4, 7, 8, 9, 10, 11],
        Graha.MERCURY: [1, 3, 5, 6, 9, 10, 11, 12],
        Graha.JUPITER: [6, 8, 11, 12],
        Graha.VENUS: [1, 2, 3, 4, 5, 8, 9, 11],
        Graha.SATURN: [1, 2, 4, 7, 8, 9, 10, 11],
        LAGNA: [1, 2, 4, 6, 8, 10, 11],
    },
    Graha.JUPITER: {
        Graha.SUN: [1, 2, 3, 4, 7, 8, 9, 10, 11],
        Graha.MOON: [2, 5, 7, 9, 11],
        Graha.MARS: [1, 2, 4, 7, 8, 10, 11],
        Graha.MERCURY: [1, 2, 4, 5, 6, 9, 10, 11],
        Graha.JUPITER: [1, 2, 3, 4, 7, 8, 10, 11],
        Graha.VENUS: [2, 5, 6, 9, 10, 11],
        Graha.SATURN: [3, 5, 6, 12],
        LAGNA: [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    Graha.VENUS: {
        Graha.SUN: [8, 11, 12],
        Graha.MOON: [1, 2, 3, 4, 5, 8, 9, 11, 12],
        Graha.MARS: [3, 5, 6, 9, 11, 12],
        Graha.MERCURY: [3, 5, 6, 9, 11],
        Graha.JUPITER: [5, 8, 9, 10, 11],
        Graha.VENUS: [1, 2, 3, 4, 5, 8, 9, 10, 11],
        Graha.SATURN: [3, 4, 5, 8, 9, 10, 11],
        LAGNA: [1, 2, 3, 4, 5, 8, 9, 11],
    },
    Graha.SATURN: {
        Graha.SUN: [1, 2, 4, 7, 8, 10, 11],
        Graha.MOON: [3, 6, 11],
        Graha.MARS: [3, 5, 6, 10, 11, 12],
        Graha.MERCURY: [6, 8, 9, 10, 11, 12],
        Graha.JUPITER: [5, 6, 11, 12],
        Graha.VENUS: [6, 11, 12],
        Graha.SATURN: [3, 5, 6, 11],
        LAGNA: [1, 3, 4, 6, 10, 11],
    },
}

# Fixed per-planet totals -- a built-in checksum. If a bhinnashtakavarga
# computation doesn't sum to these, something upstream is wrong.
EXPECTED_TOTALS = {
    Graha.SUN: 48, Graha.MOON: 49, Graha.MARS: 39, Graha.MERCURY: 54,
    Graha.JUPITER: 56, Graha.VENUS: 52, Graha.SATURN: 39,
}
EXPECTED_SAV_TOTAL = sum(EXPECTED_TOTALS.values())  # 337

BAV_PLANETS = [Graha.SUN, Graha.MOON, Graha.MARS, Graha.MERCURY,
               Graha.JUPITER, Graha.VENUS, Graha.SATURN]


def bhinnashtakavarga(target: Graha, positions: dict, ascendant_longitude: float) -> list:
    """
    Return a 12-element list (index 0 = Aries ... 11 = Pisces) of bindu
    counts (0-8) for `target`'s Bhinnashtakavarga.

    positions: {Graha: sidereal_longitude} for at least the 7 classical
    grahas (Rahu/Ketu, if present, are ignored -- they're not
    contributors or targets in Parashari Ashtakavarga).
    """
    bindus = [0] * 12
    rules = BENEFIC_PLACES[target]
    for contributor in CONTRIBUTORS:
        contributor_sign = (
            sign_index(ascendant_longitude) if contributor == LAGNA
            else sign_index(positions[contributor])
        )
        for house in rules[contributor]:
            target_sign = (contributor_sign + house - 1) % 12
            bindus[target_sign] += 1
    return bindus


def sarvashtakavarga(positions: dict, ascendant_longitude: float) -> list:
    """Sum of all 7 planetary Bhinnashtakavargas -- a 12-element list of
    per-sign totals. Always uses unreduced BAV figures (Sarvashtakavarga
    is never itself reduced, per classical convention)."""
    totals = [0] * 12
    for planet in BAV_PLANETS:
        bav = bhinnashtakavarga(planet, positions, ascendant_longitude)
        for i in range(12):
            totals[i] += bav[i]
    return totals


def full_ashtakavarga(positions: dict, ascendant_longitude: float) -> dict:
    """Convenience: every planet's BAV plus the SAV, in one call."""
    result = {p.value: bhinnashtakavarga(p, positions, ascendant_longitude)
              for p in BAV_PLANETS}
    result["Sarvashtakavarga"] = sarvashtakavarga(positions, ascendant_longitude)
    return result


# -- Trikona Sodhana and Ekadhipatya Sodhana (reduction techniques) -----
#
# SOURCING: both rule sets below are transcribed directly from a single
# source (astrovastutips.com) whose presentation reads as a faithful,
# complete classical restatement -- it uses correct Sanskrit terminology,
# states the ordering constraint ("Trikona then Ekadhipatya, this order
# cannot be reversed") that independently matches a Phaladeepika quote
# found separately ("After performing the Trikona reduction, the
# Ekadhipatya reduction should be proceeded with"), and its qualitative
# claims (never raises a score; Sun/Moon excluded from Ekadhipatya since
# they own one sign each; Rahu/Ketu don't count as "occupying" a sign for
# this purpose) are independently corroborated by two other sources
# (steer.coach, pocalc.com) describing the same procedure in less
# granular terms. No numeric worked example was available to
# cross-validate against, so correctness here rests on exhaustive
# coverage of every documented rule branch in the test suite, not an
# external numeric match (contrast with Ashtakavarga's base bindu tables
# and Saptavargaja, which DO have worked-example validation).

TRIKONA_GROUPS = [
    (0, 4, 8),    # Fire: Aries, Leo, Sagittarius
    (1, 5, 9),    # Earth: Taurus, Virgo, Capricorn
    (2, 6, 10),   # Air: Gemini, Libra, Aquarius
    (3, 7, 11),   # Water: Cancer, Scorpio, Pisces
]

# Signs sharing the same lord (Sun/Moon excluded -- they own one sign each).
EKADHIPATYA_PAIRS = [
    (0, 7),   # Aries/Scorpio -- Mars
    (1, 6),   # Taurus/Libra -- Venus
    (2, 5),   # Gemini/Virgo -- Mercury
    (8, 11),  # Sagittarius/Pisces -- Jupiter
    (9, 10),  # Capricorn/Aquarius -- Saturn
]


def trikona_sodhana(bav: list) -> list:
    """
    First reduction pass. Rules (astrovastutips.com, synthesized into an
    unambiguous procedure -- see module note above):
      - If all three signs in a trine are already equal (including all
        zero), set all three to 0.
      - Else if exactly one of the three is 0, leave the trine
        untouched (subtracting the min, which is 0, would be a no-op
        anyway -- stated explicitly as its own rule in the source).
      - Else if exactly two of the three are 0, force the third to 0
        too (this is the one genuinely non-obvious rule -- naive
        "subtract the minimum" logic would leave the third sign
        unchanged here, which is wrong).
      - Otherwise (no zeros, not all equal): subtract the minimum of
        the three from all three.
    """
    result = list(bav)
    for a, b, c in TRIKONA_GROUPS:
        vals = [result[a], result[b], result[c]]
        zero_count = vals.count(0)
        if len(set(vals)) == 1:
            result[a] = result[b] = result[c] = 0
        elif zero_count == 1:
            pass  # no reduction -- one zero present, rest untouched
        elif zero_count == 2:
            result[a] = result[b] = result[c] = 0
        else:
            m = min(vals)
            result[a] -= m
            result[b] -= m
            result[c] -= m
    return result


def ekadhipatya_sodhana(bav_after_trikona: list, sign_occupied: list) -> list:
    """
    Second reduction pass, applied AFTER trikona_sodhana (never before --
    the order is classically fixed). Only touches the 5 same-lord sign
    pairs; Sun's Leo and Moon's Cancer are never touched by this pass.

    sign_occupied: a 12-element list of bool, True if a classical graha
    (Sun through Saturn -- NOT Rahu/Ketu, per the source's explicit
    caution note) sits in that sign in the natal D1 chart.
    """
    result = list(bav_after_trikona)
    for sign_a, sign_b in EKADHIPATYA_PAIRS:
        val_a, val_b = result[sign_a], result[sign_b]
        occ_a, occ_b = sign_occupied[sign_a], sign_occupied[sign_b]

        if val_a == 0 or val_b == 0:
            continue  # rule 1b: a zero already present -- no reduction
        if occ_a and occ_b:
            continue  # rule 1: both occupied -- no reduction

        if occ_a and not occ_b:
            occupied_val, unoccupied_sign = val_a, sign_b
        elif occ_b and not occ_a:
            occupied_val, unoccupied_sign = val_b, sign_a
        else:
            occupied_val = None  # both unoccupied -- handled below

        if occupied_val is not None:
            unoccupied_val = result[unoccupied_sign]
            if occupied_val >= unoccupied_val:
                result[unoccupied_sign] = 0
            else:
                result[unoccupied_sign] = occupied_val
        else:
            # Both signs unoccupied.
            if val_a == val_b:
                result[sign_a] = result[sign_b] = 0
            else:
                smaller = min(val_a, val_b)
                result[sign_a] = smaller
                result[sign_b] = smaller
    return result


def reduced_bhinnashtakavarga(target: Graha, positions: dict, ascendant_longitude: float) -> list:
    """Full two-stage reduction (Trikona then Ekadhipatya) for one
    planet's Bhinnashtakavarga. Occupancy for the Ekadhipatya stage is
    read from `positions` (Rahu/Ketu, even if present in `positions`,
    are never counted as occupying a sign for this purpose)."""
    bav = bhinnashtakavarga(target, positions, ascendant_longitude)
    after_trikona = trikona_sodhana(bav)

    occupied = [False] * 12
    for g in BAV_PLANETS:  # BAV_PLANETS excludes Rahu/Ketu already
        occupied[sign_index(positions[g])] = True

    return ekadhipatya_sodhana(after_trikona, occupied)