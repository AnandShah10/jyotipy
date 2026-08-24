# JyotiPy

A pure-Python Vedic (Jyotish) astrology library. No C extensions, no
ephemeris kernel downloads, works on Python 3.8 through 3.14.

Built as an alternative to `pyswisseph` for two reasons: pyswisseph's
AGPL license is a blocker for closed/commercial use, and `pip install`
frequently breaks on newer Python versions since it needs to compile a C
extension against a specific interpreter ABI. JyotiPy has neither
problem — planetary positions come from
[`PyMeeus`](https://pypi.org/project/PyMeeus/) (VSOP87 + ELP2000-82,
pure Python), and everything else is plain Python arithmetic.

## Install

```bash
pip install jyotipy   # not published yet -- see "Publishing" below
# or, from source:
pip install -e .
```

## Quick start

```python
from datetime import datetime
from jyotipy import BirthChart

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

## What's implemented (v0.1)

| Area | Status |
|---|---|
| Tropical planetary positions (Sun, Moon, Mercury-Saturn) | Done, via PyMeeus |
| Rahu/Ketu (mean node default, true node optional) | Done |
| Ayanamsa: Lahiri, True Chitrapaksha, KP-Newcomb, Raman | Done (see accuracy notes) |
| Ascendant / Midheaven | Done |
| Houses: Whole Sign, Equal, Porphyry | Done |
| Nakshatra + Pada | Done |
| Divisional charts: D1, D2, D3, D4, D7, D9, D10, D12 | Done |
| Divisional charts: D16, D20, D24, D27, D30, D40, D45, D60 | **Not implemented** — raises `NotImplementedError`, see below |
| Vimshottari Mahadasha + Antardasha | Done |
| Yogas: Pancha Mahapurusha, Gajakesari, Budhaditya, Chandra-Mangal, Sunapha/Anapha/Durudhara, Kemadruma (simplified), Neechabhanga (simplified, primary rule only) | Done, deliberately conservative set |
| Panchanga: Tithi, Vara, Nakshatra, Nitya Yoga, Karana | Done |
| Placidus / true Sripati houses | **Not implemented** |

## Accuracy notes — read this before using it for real work

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

1. D16-D60 divisional charts (needs primary-source verification, not
   guesswork)
2. Iterative Placidus / true Sripati house systems
3. Ashtakavarga
4. Transit (Gochara) analysis
5. Shadbala (planetary strength)
6. Optional high-precision backend (JPL DE440 via `skyfield`) for anyone
   who wants sub-arcsecond agreement with Swiss Ephemeris and doesn't
   mind the kernel download

## License

MIT. Depends on `PyMeeus` (LGPLv3) as an unmodified runtime dependency —
this doesn't affect JyotiPy's own license, but if you vendor/fork PyMeeus
itself rather than depending on it normally, LGPL terms apply to that
fork.

## Publishing

Not yet published to PyPI. To publish:

```bash
pip install build twine
python -m build
twine upload dist/*
```

Bump `version` in `pyproject.toml` first, and fix the placeholder GitHub
URLs.
