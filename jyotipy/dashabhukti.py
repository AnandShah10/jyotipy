"""
Dasha/Bhukti activation: layers planetary STRENGTH (Shadbala) on top of
Vimshottari TIMING (which planets currently rule) to judge which of the
two active period lords actually dominates the period's results, and
whether either is even strong enough to deliver much at all.

SOURCING:
  - The core mechanism -- comparing the Dasha lord's and Bhukti lord's
    Shadbala to see which dominates -- is a DIRECT worked example quoted
    from Raman himself: "Suppose... a person is undergoing Sun Dasa and
    Moon Bhukti... If the Sun is more powerful than the Moon, then the
    results likely to happen would be predominantly those indicated by
    the Sun." This isn't a reconstruction; it's Raman's own stated
    method for exactly this question.
  - Minimum Shadbala thresholds (a planet below its threshold is
    "Balaheena" -- too weak to deliver its significations reliably) are
    cross-checked against 3 independent sources agreeing exactly:
        Sun 390, Moon 360, Mars 300, Mercury 420, Jupiter 390,
        Venus 330, Saturn 300  (Virupas)
    A fourth source gave a different figure for Mars (390) that
    conflicts with the other three and looks like a transcription slip
    (it also lists 390 twice more, for Sun and Jupiter) -- discounted as
    an outlier rather than averaged in.

WHAT THIS DOES NOT DO: this is a strength/dominance judgment layered on
top of the Dasha and Gochara systems, not a full synthesis of Raman's
complete predictive method (which also weighs house lordships,
functional benefic/malefic status per ascendant, and specific classical
yogas -- none of which this function attempts to re-derive).
"""

from .constants import Graha

MINIMUM_SHADBALA_VIRUPAS = {
    Graha.SUN: 390, Graha.MOON: 360, Graha.MARS: 300, Graha.MERCURY: 420,
    Graha.JUPITER: 390, Graha.VENUS: 330, Graha.SATURN: 300,
}


def meets_minimum_shadbala(planet: Graha, shadbala_total_virupas: float):
    """True/False if the planet has a known threshold; None if it
    doesn't (Rahu/Ketu -- Shadbala and its thresholds are defined only
    for the 7 classical grahas)."""
    threshold = MINIMUM_SHADBALA_VIRUPAS.get(planet)
    if threshold is None:
        return None
    return shadbala_total_virupas >= threshold


def dasha_bhukti_dominance(dasha_lord: Graha, dasha_shadbala: float,
                            bhukti_lord: Graha, bhukti_shadbala: float) -> dict:
    """
    Per Raman's own worked example: whichever of the Dasha lord and
    Bhukti lord has the higher Shadbala dominates the period's actual
    results. Also flags whether each individually clears its own
    minimum threshold (a period can be "dominated" by a lord that's
    itself still too weak to deliver much -- these are separate
    questions, both reported).
    """
    dasha_meets_min = meets_minimum_shadbala(dasha_lord, dasha_shadbala)
    bhukti_meets_min = meets_minimum_shadbala(bhukti_lord, bhukti_shadbala)

    if dasha_shadbala > bhukti_shadbala:
        dominant, weaker = dasha_lord, bhukti_lord
    elif bhukti_shadbala > dasha_shadbala:
        dominant, weaker = bhukti_lord, dasha_lord
    else:
        dominant, weaker = None, None  # tie -- Raman's example doesn't cover this case

    return {
        "dasha_lord": dasha_lord, "dasha_shadbala": round(dasha_shadbala, 3),
        "dasha_meets_minimum": dasha_meets_min,
        "bhukti_lord": bhukti_lord, "bhukti_shadbala": round(bhukti_shadbala, 3),
        "bhukti_meets_minimum": bhukti_meets_min,
        "dominant_lord": dominant,
        "note": ("Results during this period will predominantly reflect the dominant "
                 "lord's significations (Raman's own stated rule), tempered by whether "
                 "either lord clears its minimum Shadbala threshold at all."),
    }


def current_dasha_bhukti_lords(mahadashas: list, antardashas_fn, at_dt) -> dict:
    """
    Given a chart's full mahadasha list (from BirthChart.mahadashas())
    and its antardasha function (BirthChart.antardashas), find which
    Mahadasha and Antardasha are active at `at_dt`.

    antardashas_fn: a callable taking one mahadasha period dict and
    returning its 9 antardasha sub-periods (i.e. pass chart.antardashas
    directly).
    """
    active_md = None
    for md in mahadashas:
        if md["start"] <= at_dt < md["end"]:
            active_md = md
            break
    if active_md is None:
        return {"mahadasha": None, "antardasha": None}

    active_ad = None
    for ad in antardashas_fn(active_md):
        if ad["start"] <= at_dt < ad["end"]:
            active_ad = ad
            break

    return {"mahadasha": active_md, "antardasha": active_ad}