# Accuracy & Scope

Read this before using JyotiPy for anything you're going to rely on.

## Planetary positions

Positions come from [PyMeeus](https://pypi.org/project/PyMeeus/), which
implements full VSOP87 (planets) and ELP2000-82 (Moon). This project's
own test suite validates PyMeeus's output against Meeus's published
worked examples, but has **not** been independently diffed against Swiss
Ephemeris output end-to-end. Cross-check a real chart against JHora or
astro.com before relying on this for client work.

## Ayanamsa

Lahiri, KP-Newcomb, and True Chitrapaksha base epochs and precession
rates are cross-checked against multiple independent public sources and
numerically validated against published 2026 reference values (accurate
to within ~0.01 degrees). Raman is implemented as a calibrated *offset*
from Lahiri rather than an independently derived base epoch -- verify
separately if your work is specifically Raman-tradition predictive work.

## Divisional charts (Varga)

D1 through D12 use unambiguous, consistently-documented classical rules
and are fully implemented. **D16 through D60 are not implemented** --
they raise `NotImplementedError`. Their classical starting-sign rules
vary across source texts, and shipping a version transcribed from memory
risked silently producing wrong charts. This is tracked as a roadmap
item pending verification against a primary source.

## Yogas

A deliberately conservative core set: Pancha Mahapurusha, Gajakesari,
Budhaditya, Chandra-Mangal, Sunapha/Anapha/Durudhara, Kemadruma, and
Neechabhanga. Kemadruma and Neechabhanga each have several classical
cancellation (bhanga) conditions across source texts -- only the single
most commonly cited primary condition is checked for each. A positive
result from either means "the raw combination is present, worth
investigating further," not a final verdict.

## Houses

Whole Sign and Equal House are exact by construction. Porphyry
(quadrant trisection) is implemented and correctly labeled as Porphyry
-- true Placidus and true Sripati require iteratively solving
diurnal/nocturnal semi-arc equations and are **not implemented**; don't
substitute Porphyry for either in KP sub-lord work.

## Vimshottari year length

Uses 365.25 days/year, a common but not universal convention among
Vimshottari calculators (others use 365.2425 or a sidereal year). Over a
120-year dasha cycle, different conventions can drift results by a few
days. Check what convention a reference tool uses if you need
bit-for-bit agreement with it.
