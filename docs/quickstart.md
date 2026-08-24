# Quickstart

## Install

```bash
pip install jyotipy
```

## Your first chart

```python
from datetime import datetime
from jyotipy import BirthChart, Graha

chart = BirthChart(
    dt=datetime(1990, 6, 15, 14, 32),   # local civil time, naive datetime
    utc_offset_hours=5.5,               # IST
    latitude=23.03, longitude=72.58,    # Ahmedabad
)

print(chart.ascendant)               # sidereal Lagna longitude, degrees
print(chart.sign_of(Graha.MOON))     # e.g. "Aquarius"
print(chart.summary())               # sign, degree, nakshatra, pada per graha
```

## Houses

```python
chart.houses("whole_sign")   # 12 cusps, sign-aligned (the Jyotish default)
chart.houses("equal")        # 12 cusps, exact 30 deg from the ascendant degree
chart.houses("porphyry")     # quadrant-trisection cusps
chart.house_of(Graha.SUN)    # which house (1-12) the Sun falls in
```

## Divisional charts (Varga)

```python
chart.varga("D9")    # Navamsha -- {Graha: sign_index}
chart.varga("D10")   # Dashamsha
```

Only D1 through D12 are implemented in v0.1 -- see {doc}`accuracy` for why
D16 and beyond currently raise `NotImplementedError`.

## Dasha

```python
mahadashas = chart.mahadashas()          # full Vimshottari sequence
first_md = mahadashas[0]
chart.antardashas(first_md)              # 9 sub-periods within it
```

## Yogas and Panchanga

```python
chart.yogas()        # Pancha Mahapurusha, Gajakesari, Budhaditya, etc.
chart.panchanga()     # Tithi, Vara, Nakshatra, Nitya Yoga, Karana
```

## Choosing an ayanamsa

```python
from jyotipy import AyanamsaSystem

chart = BirthChart(
    dt=datetime(1990, 6, 15, 14, 32),
    utc_offset_hours=5.5,
    latitude=23.03, longitude=72.58,
    ayanamsa=AyanamsaSystem.KP_NEWCOMB,   # default is AyanamsaSystem.LAHIRI
)
```
