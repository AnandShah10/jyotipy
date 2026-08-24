# JyotiPy

[![PyPI version](https://img.shields.io/pypi/v/jyotipy.svg?logo=pypi)](https://pypi.org/project/jyotipy/)
[![Python versions](https://img.shields.io/pypi/pyversions/jyotipy.svg?logo=python)](https://pypi.org/project/jyotipy/)
[![Documentation Status](https://readthedocs.org/projects/jyotipy/badge/?version=latest)](https://jyotipy.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/github/license/AnandShah10/jyotipy.svg)](https://github.com/AnandShah10/jyotipy/blob/master/LICENSE)

Pure-Python Vedic (Jyotish) astrology library. Computes sidereal planetary positions, ascendant, houses, vargas, dashas, panchanga, and a conservative set of yogas with zero C extensions or external ephemeris files.

Built as a permissive-license alternative to `pyswisseph`. All computations use [`PyMeeus`](https://pypi.org/project/PyMeeus/) for planetary positions (VSOP87 + ELP2000-82) followed by pure-Python ayanamsa, house, and yoga logic. Supports Python 3.8+.

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
from jyotipy.chart import BirthChart

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

## Features

- **Planetary positions**: Sun–Saturn + Rahu/Ketu (mean node default; true node optional) using PyMeeus (VSOP87/ELP2000)
- **Ayanamsa**: Lahiri (default), True Chitrapaksha, KP-Newcomb, Raman
- **Lagna & Houses**: Whole-sign, Equal, Porphyry (Placidus and Sripati planned)
- **Nakshatras**: With pada and full support
- **Divisional charts (Vargas)**: D1–D12 fully implemented using standard rules; D16+ raise `NotImplementedError` (see Accuracy Notes)
- **Dashas**: Vimshottari Mahadasha and Antardasha
- **Yogas**: Deliberately conservative core set (see `jyotipy.yogas` for details):
  - Pancha Mahapurusha (Ruchaka, Bhadra, Hamsa, Malavya, Sasa)
  - Gajakesari, Budhaditya (Sun-Mercury), Chandra-Mangal (Moon-Mars)
  - Sunapha, Anapha, Durudhara, Kemadruma (raw), Neechabhanga candidates
  - *Note*: Many classical cancellation rules and variant definitions are not auto-applied; results are candidates for further analysis.
- **Panchanga**: Tithi, Vara, Nakshatra, Nitya Yoga, Karana

## Accuracy Notes

- **Planetary positions**: PyMeeus implements full VSOP87 (planets) and
  ELP2000-82 (Moon), validated in this project against Meeus's own
  published worked examples. Expect arcsecond-to-sub-arcminute agreement
  with Swiss Ephemeris for the modern era. Not independently verified
  against Swiss Ephemeris output in this repo (no network access to fetch
  a reference dataset during development) — **cross-check a real chart
  against JHora or astro.com before relying on this for client work.**
- **Ayanamsa**: Lahiri/KP-Newcomb/True Chitrapaksha base epochs and rates
  are cross-checked against multiple independent public sources and
  numerically validated to match published 2026 reference values to
  ~0.01°. Raman is implemented as a calibrated *offset* from Lahiri
  rather than an independently derived base epoch — verify separately if
  your work is Raman-tradition-specific.
- **Divisional charts D16 and beyond**: deliberately not implemented.
  Their classical starting-sign rules vary across source texts and are
  easy to misremember in ways that silently produce wrong charts. D1
  through D12 (the most commonly used divisions in practice, including
  Navamsha and Dashamsha) are implemented and use unambiguous, widely
  agreed rules.
- **Kemadruma and Neechabhanga**: both have several classical
  cancellation (bhanga) conditions in the source texts; only the single
  most commonly cited primary condition is checked for each. A `True`/
  candidate result means "the raw combination is present, worth checking
  further" — not a final verdict.
- **Vimshottari year length**: uses 365.25 days/year, a common but not
  universal convention. If you need bit-for-bit agreement with a specific
  tool, check what year length it uses.

## Roadmap

- D16–D60 divisional charts (requires careful primary-source verification)
- Placidus and true Sripati house systems
- Ashtakavarga
- Gochara (transit) analysis
- Shadbala (planetary strength calculations)
- Optional high-precision backend using JPL DE440 via `skyfield`

## License

[MIT License](https://github.com/AnandShah10/jyotipy/blob/master/LICENSE) (see the `LICENSE` file in the GitHub repository).

JyotiPy depends on [`PyMeeus`](https://pypi.org/project/PyMeeus/) (LGPLv3) as an unmodified runtime dependency. This does not change JyotiPy's own MIT license, but if you vendor or fork PyMeeus itself, the LGPL terms apply to that portion.

**Full documentation**: [https://jyotipy.readthedocs.io](https://jyotipy.readthedocs.io)

Source code, examples, and issue reports are at the
[GitHub repository](https://github.com/AnandShah10/jyotipy).
