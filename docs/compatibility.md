# Compatibility (Guna Milan)

JyotiPy implements the classical **Ashtakoot Guna Milan** system: the 36-point
marriage-compatibility method used throughout Hindu astrology, built from eight
independent "kootas" scored between two people's Moon positions.

## Usage

Compatibility is the one operation in JyotiPy that involves **two** charts
rather than one, so it's a module-level function, not a `BirthChart` method.

```python
from datetime import datetime
from jyotipy import BirthChart, guna_milan

bride = BirthChart(
    dt=datetime(1992, 3, 10, 9, 15),
    utc_offset_hours=5.5,
    latitude=19.0760, longitude=72.8777,   # Mumbai
)
groom = BirthChart(
    dt=datetime(1990, 6, 15, 14, 32),
    utc_offset_hours=5.5,
    latitude=23.0225, longitude=72.5714,   # Ahmedabad
)

report = guna_milan(bride, groom)

print(report["total_score"], "/", report["max_score"])      # e.g. 31.5 / 36
print(report["meets_traditional_minimum"])                   # True if >= 18

for koota, data in report["kootas"].items():
    print(koota, data["score"], "/", data["max"])
```

If you already have raw sidereal Moon longitudes rather than full charts, call
`jyotipy.compatibility.guna_milan(bride_moon_longitude, groom_moon_longitude)`
directly.

### Why "bride" and "groom"?

Several kootas (Varna and Tara especially) are **directional** -- swapping the
two people can change the score. The traditional bride/groom framing is used
because it's what the source tables are written in, not because anything here
assumes gender. Assign the two roles however fits your use case, but be aware
that the assignment matters.

## The eight kootas

| Koota | Max points | Based on |
|---|---|---|
| Varna | 1 | Moon sign's caste-like category (Brahmin/Kshatriya/Vaishya/Shudra) |
| Vashya | 2 | Moon sign's "control" category (human, quadruped, water, wild, insect) |
| Tara | 3 | Count between the two Moon nakshatras |
| Yoni | 4 | Animal symbol assigned to each Moon nakshatra |
| Graha Maitri | 5 | Friendship between the two Moon-sign lords |
| Gana | 6 | Temperament category of each Moon nakshatra (Deva/Manushya/Rakshasa) |
| Bhakoot | 7 | Distance between the two Moon signs |
| Nadi | 8 | Physiological category of each Moon nakshatra (Aadi/Madhya/Antya) |

The traditionally recommended minimum total is **18 out of 36**.

## Reading the result

Each entry in `report["kootas"]` includes its own `score` and `max`, plus the
specific inputs that produced that score (for example, Nadi reports both
people's Nadi category, Bhakoot reports the sign distance and whether a dosha
was found or cancelled). This is deliberate: a bare total hides which kootas
failed, and in traditional practice *which* koota failed often matters more
than the sum -- Nadi and Bhakoot in particular carry much of the weight in how
practitioners actually interpret a match.

A well-known real-world pattern worth knowing about: two people with the
**same Moon nakshatra** will always score 0 on Nadi (same category) and 0 on
Tara (same-star counts as the first position, scored as unfavourable), so even
an otherwise-perfect match tops out well below 36. This isn't a quirk of this
implementation -- it falls naturally out of the classical rules, and is the
reason same-nakshatra pairings are traditionally treated with caution.

## Confidence by koota

This was one of the most sourcing-intensive features in the library. Several
of the eight tables had real disagreement between sources that needed resolving
rather than picking arbitrarily. Where confidence differs, it's noted here
rather than hidden:

**Strongly cross-validated**
- **Varna** -- sign-to-category assignment confirmed unanimously by 10
  independent sources.
- **Gana** -- the complete 27-nakshatra assignment was checked against a second
  source via 7 independent spot-checks, with zero discrepancies.
- **Nadi** -- the 27-nakshatra assignment follows a repeating six-nakshatra
  pattern (Aadi, Madhya, Antya, Antya, Madhya, Aadi). This pattern was
  discovered by testing it against individually-confirmed nakshatras from two
  independent sources and matched all 17 data points with no exceptions, which
  is strong enough to generate the full list from the pattern.
- **Bhakoot** -- the 2-12 / 5-9 / 6-8 dosha rule is confirmed by 7+ sources.
- **Vashya** -- a complete numeric point matrix was found directly (not just
  qualitative friend/enemy descriptions), including the half-sign splits for
  Sagittarius and Capricorn.
- **Tara** -- the mechanical scoring rule is confirmed by 8 independent sources
  with matching worked examples.

**Implemented with documented caveats**
- **Yoni** -- the nakshatra-to-animal assignment is well established, and the
  seven hostile pairs (Horse-Buffalo, Elephant-Lion, Sheep-Monkey,
  Serpent-Mongoose, Dog-Deer, Cat-Rat, Cow-Tiger) are each independently
  corroborated. The intermediate friendly/neutral/unfriendly tiers rest on a
  single source (after correcting a mistranslation in it -- see the module
  docstring for the details) and are a notch below the library's usual
  cross-validation standard.
- **Graha Maitri** -- reuses the same natural-planetary-friendship table already
  validated for Saptavargaja Bala. The *point scale* applied to it (5 for same
  lord or mutual friends, 4 for one-sided friendship, 3 for neutral, 1 for
  one-sided enmity, 0 for mutual enemies) is a commonly-cited approximation
  rather than something independently re-verified here.
- **Bhakoot cancellation** -- only the single most universally-cited
  cancellation (both Moon signs share the same ruling planet) is implemented.
  Several other cancellation conditions exist in the wider literature and are
  deliberately not implemented.
- **Tara** -- the scoring rule treats position 1 (same nakshatra) as
  unfavourable, matching the mechanical formula every source gives, even though
  classical Tara *theory* describes that position more ambiguously. This is a
  documented simplification, not an oversight.

## What this does *not* do

Guna Milan is one part of traditional marriage matching, not the whole of it.
Practitioners also typically examine Manglik (Kuja) dosha, the strength and
placement of the seventh house and its lord, Dasha compatibility, and more.
None of that is implemented here -- this module scores the eight kootas and
nothing else, and a high score should not be read as a complete compatibility
verdict.
