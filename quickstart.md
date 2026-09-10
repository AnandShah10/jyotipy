<!--
Append everything below to the END of your existing docs/quickstart.md.
-->

## Ashtakavarga (new in 0.2)

```python
chart.ashtakavarga(Graha.SUN)      # Sun's raw Bhinnashtakavarga, 12-sign bindu list
chart.ashtakavarga()                # every planet + Sarvashtakavarga
chart.reduced_ashtakavarga(Graha.SUN)  # after Trikona + Ekadhipatya Sodhana
```

## Transits and Dasha/Bhukti activation (new in 0.2)

```python
from datetime import datetime

chart.transits(datetime(2026, 9, 1, 12, 0), transit_utc_offset_hours=5.5)
chart.sade_sati(datetime(2026, 9, 1, 12, 0), transit_utc_offset_hours=5.5)
chart.dasha_bhukti_activation(datetime(2026, 9, 1, 12, 0))
```

## Shadbala (new in 0.2)

```python
chart.shadbala(Graha.SUN)   # single-planet report (Yuddha Bala not resolved here)
chart.full_shadbala()       # all 7 planets, with Yuddha Bala correctly applied
```

## More house systems (new in 0.2)

```python
chart.houses("placidus")
chart.houses("sripati")
```
