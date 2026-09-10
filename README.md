# JyotiPy

[![PyPI version](https://img.shields.io/pypi/v/jyotipy.svg?logo=pypi)](https://pypi.org/project/jyotipy/)
[![Python versions](https://img.shields.io/pypi/pyversions/jyotipy.svg?logo=python)](https://pypi.org/project/jyotipy/)
[![License: MIT](https://img.shields.io/github/license/AnandShah10/jyotipy.svg)](https://github.com/AnandShah10/jyotipy/blob/master/LICENSE)

Pure-Python Vedic (Jyotish) astrology library. Computes sidereal planetary positions, ascendant, houses, divisional charts, dashas, panchanga, transits, Ashtakavarga, Shadbala, and a conservative set of yogas with zero C extensions or external ephemeris files.

Built as a permissive-license alternative to `pyswisseph`. All computations use [`PyMeeus`](https://pypi.org/project/PyMeeus/) for planetary positions (VSOP87 + ELP2000-82) followed by pure-Python ayanamsa, house, dasha, and strength-system logic. Supports Python 3.8+.

## Installation

```bash
pip install jyotipy
```

Or install from source:

```bash
git clone https://github.com/AnandShah10/jyotipy.git
cd jyotipy
pip install -e .
```

## Quick Start

```python
from datetime import datetime
from jyotipy import BirthChart, Graha

chart = BirthChart(
    dt=datetime(1990, 6, 15, 14, 32),
    utc_offset_hours=5.5,
    latitude=23.03, longitude=72.58,   # Ahmedabad
)

print(chart.summary())          # sign, degree, nakshatra, pada per graha
print(chart.ascendant)          # sidereal Lagna longitude
print(chart.houses("whole_sign"))
print(chart.varga("D9"))        # Navamsha
print(chart.mahadashas()[:3])   # first 3 Vimshottari mahadashas
print(chart.yogas())
print(chart.panchanga())
```

### New in 0.2

```python
chart.reduced_ashtakavarga(Graha.SUN)                # Bhinnashtakavarga after Trikona + Ekadhipatya Sodhana
chart.transits(datetime(2026, 9, 1, 12, 0), 5.5)     # Gochara + Vedha-aware transit report
chart.sade_sati(datetime(2026, 9, 1, 12, 0), 5.5)    # Sade Sati / Kantaka Sani / Ashtama Sani status
chart.dasha_bhukti_activation(datetime(2026, 9, 1))  # which period lord dominates, via Shadbala
chart.full_shadbala()                                # all six Shadbala components, all 7 planets, Yuddha Bala applied
chart.houses("placidus")                             # or "sripati"
```

See [`CHANGELOG.md`](CHANGELOG.md) for the full list of what shipped in 0.2.

## What's implemented (v0.2)

| Area | Status |
|---|---|
| Tropical planetary positions (Sun, Moon, Mercury-Saturn) | Done, via PyMeeus |
| Rahu/Ketu (mean node default, true node optional) | Done |
| Ayanamsa: Lahiri, True Chitrapaksha, KP-Newcomb, Raman | Done -- Raman now independently sourced (397 CE epoch), not a Lahiri offset |
| Ascendant / Midheaven | Done |
| Houses: Whole Sign, Equal, Porphyry, **Placidus**, **Sripati** | Done -- see Accuracy notes for two honest caveats |
| Nakshatra + Pada | Done |
| Divisional charts: **all 16 vargas, D1 through D60** | Done |
| Vimshottari Mahadasha + Antardasha | Done |
| **Dasha/Bhukti activation weighting** (which period lord dominates, via Shadbala comparison) | Done |
| Yogas: Pancha Mahapurusha, Gajakesari, Budhaditya, Chandra-Mangal, Sunapha/Anapha/Durudhara, Kemadruma, Neechabhanga | Done, deliberately conservative set |
| Panchanga: Tithi, Vara, Nakshatra, Nitya Yoga, Karana | Done |
| **Ashtakavarga**: Bhinnashtakavarga, Sarvashtakavarga, Trikona Sodhana, Ekadhipatya Sodhana | Done |
| **Transit/Gochara**: good/bad houses from Moon, Vedha, Sade Sati, Ashtakavarga-qualified verdicts | Done |
| **Shadbala: all six components** (Sthana, Dig, Kala, Chesta, Naisargika, Drik) | Done -- see Accuracy notes for two narrow open items |

## Accuracy notes -- read this before using it for real work

- **Planetary positions**: PyMeeus implements full VSOP87 (planets) and ELP2000-82 (Moon), validated in this project against Meeus's own published worked examples. Cross-check a real chart against JHora or astro.com before relying on this for client work.
- **Ayanamsa**: Lahiri/KP-Newcomb/True Chitrapaksha are cross-checked against multiple independent public sources and numerically validated against published reference values. Raman is now independently sourced from its own base epoch (397 CE) and precession rate, confirmed by 7 independent sources including B.V. Raman's grandson.
- **Divisional charts**: all 16 vargas (D1-D60) are implemented and cross-sourced. D60 specifically has a documented, unresolved disagreement between two classical methods in the wider literature; this implementation uses the one modern software (JHora) actually uses -- see `varga.py` for the alternate reading.
- **Houses**: Whole Sign and Equal House are exact by construction. Porphyry, Placidus, and Sripati are all implemented, but Placidus in particular required unusually extensive debugging -- see `houses.py`'s module comments for the full story if you want to understand exactly what's verified (boundary conditions to numerical precision, universal house-numbering convention against real Swiss Ephemeris output) versus what has no external numeric example to check against (the final 12-cusp output end-to-end). Sripati has one known quirk: for some ordinary, non-polar charts, its House 1 cusp doesn't sit exactly at the true Ascendant, because the real reference algorithm (transcribed directly from Swiss Ephemeris source) includes a swap condition that triggers more broadly than its own documentation suggests.
- **Ashtakavarga**: the base bindu tables and both reduction techniques (Trikona/Ekadhipatya Sodhana) are implemented. The base tables are validated against a fully worked B.V. Raman example (all 7 planets plus Sarvashtakavarga matched exactly). The two reductions don't have an external worked example to check against; confidence rests on exhaustive coverage of every documented rule branch in the test suite instead.
- **Shadbala**: all six classical components (Sthana, Dig, Kala, Chesta, Naisargika, Drik) are now implemented. Two narrow open items remain: Yuddha Bala's victor rule doesn't implement a secondary "Venus always wins" exception some sources describe, and Drik Bala's formula was reconstructed from a worked reference grid (not a primary text) -- both documented in their respective modules (`yuddhabala.py`, `drikbala.py`).
- **Transit/Gochara**: the base good/bad-house and Vedha tables are cross-validated against multiple sources and a full worked example. Dasha/Bhukti activation weighting layers Shadbala-based strength judgment on top, per B.V. Raman's own stated method, but doesn't attempt his complete predictive synthesis (house lordships, functional benefic/malefic status, classical yogas).
- **Vimshottari year length**: uses 365.25 days/year, a common but not universal convention. Check what a reference tool uses if you need bit-for-bit agreement with it.

## Roadmap

1. Nadi astrology, Prashna (horary), Muhurta (electional), Varshaphal/Tajika (annual charts), Compatibility/Synastry (Guna Milan) -- none started yet
2. A CLI for the library
3. Full documentation coverage as new modules are added (currently up to date as of 0.2.0)

## License

[MIT License](https://github.com/AnandShah10/jyotipy/blob/master/LICENSE) (see the `LICENSE` file in the GitHub repository).

JyotiPy depends on [`PyMeeus`](https://pypi.org/project/PyMeeus/) (LGPLv3) as an unmodified runtime dependency. This does not change JyotiPy's own MIT license, but if you vendor or fork PyMeeus itself, the LGPL terms apply to that portion.

**Full documentation**: [https://jyotipy.readthedocs.io](https://jyotipy.readthedocs.io)

Source code, examples, and issue reports are at the
[GitHub repository](https://github.com/AnandShah10/jyotipy).