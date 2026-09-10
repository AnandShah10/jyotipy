# Changelog

## 0.2.0

### Added
- **Divisional charts**: D16, D20, D24, D27, D30, D40, D45, D60 (all 16 vargas now implemented, up from D1-D12 in 0.1.0). Each cross-checked against 2-4 independent sources; D30 and D60 additionally validated against fully worked numeric examples pulled from those sources.
- **Ashtakavarga reductions**: Trikona Sodhana and Ekadhipatya Sodhana, the two classical techniques for reducing raw Bhinnashtakavarga bindu counts for predictive use. `BirthChart.reduced_ashtakavarga()`.
- **Dasha/Bhukti-weighted transits**: `BirthChart.dasha_bhukti_activation()` compares the active Mahadasha and Antardasha lords' Shadbala to judge which dominates a period's results, per B.V. Raman's own stated method. Also corrected an earlier unsourced Ashtakavarga bindu threshold in the base transit report (was an unsourced >=5, now a properly-sourced >=4).
- **Shadbala, now complete across all six components** (was Sthana/Dig/Naisargika only in 0.1.0):
  - Sthana Bala's Saptavargaja sub-component (`saptavargaja.py`) -- the largest and previously-missing piece.
  - Kala Bala in full: Nathonnata, Paksha, Tribhaga, Ayana, Varsha/Masa/Dina/Hora, and Yuddha Bala (`kalabala.py`, `yuddhabala.py`).
  - Chesta Bala for all 7 classical grahas (Sun/Moon via BPHS substitution rule, the other 5 via actual orbital motion).
  - Drik Bala (`drikbala.py`), reconstructed from a fully worked reference grid after extensive sourcing difficulty.
  - `BirthChart.full_shadbala()` for a mutually-consistent, war-adjusted set across all 7 planets.
- **True Placidus houses** (`houses("placidus")`), via iterative semi-arc trisection. Required extensive debugging -- see `houses.py` module comments for the full story, including two real bugs found and fixed via direct numerical testing against boundary conditions.
- **Sripati houses** (`houses("sripati")`), transcribed directly from the real Swiss Ephemeris source code rather than prose descriptions.
- **Raman ayanamsa**, now independently sourced (397 CE zero-epoch, 50 1/3 arcsec/year precession rate, confirmed by 7 independent sources including B.V. Raman's own grandson) rather than a calibrated offset from Lahiri.

### Fixed
- **Porphyry houses**: a real, previously undetected bug where certain charts (specifically when MC's raw longitude exceeds the Ascendant's) caused houses 1, 5, and 9 to collapse to nearly the same degree. Found while building Sripati on top of the Porphyry function. Fixed by deriving each quadrant from its own signed short arc.

### Notes
- Every new feature above follows the project's existing standard: cross-sourced from multiple independent references where possible, validated against worked numeric examples where available, and explicitly flagged (never silently guessed) where a genuine sourcing gap remains. See each module's own docstring for its specific confidence level and any open caveats.
- Two known gaps remain in Yuddha Bala (the "Venus always wins" exception some secondary sources describe isn't implemented) and Sripati (a real ac-swap quirk in the reference algorithm means House 1 doesn't always sit exactly at the true Ascendant for some charts) -- both documented in their respective modules.
