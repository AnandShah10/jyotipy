"""
Vimshottari Dasha: the 120-year planetary period system used for timing
predictions, computed from the Moon's nakshatra position at birth.

Algorithm (standard, unchanged across every classical/software source):
  1. Find the Moon's nakshatra at birth and its ruling lord.
  2. The FIRST (birth) mahadasha belongs to that lord, but is only run for
     the *remaining* fraction of that lord's full period -- proportional
     to how far the Moon still has to travel through the nakshatra.
  3. Every subsequent mahadasha runs for its lord's full period, cycling
     through VIMSHOTTARI_ORDER, wrapping after Mercury back to Ketu.
  4. Each mahadasha subdivides into 9 antardashas (one per graha, same
     order, starting from the mahadasha's own lord), with antardasha
     duration = mahadasha_duration * (antardasha_lord_years / 120).

One convention note: "1 year" here means 365.25 days (a common convention
in Vimshottari calculators). Some software uses 365.2425 (Gregorian mean)
or a sidereal year (~365.2564 days); over a 120-year cycle these
conventions can drift results by a few days. If you need bit-for-bit
agreement with a specific reference tool, check which year-length it uses.
"""

from datetime import timedelta
from pymeeus.Epoch import Epoch

from .constants import VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS, NAKSHATRA_LORDS, Graha
from .nakshatra import nakshatra_index, DEG_PER_NAKSHATRA
from .utils import norm360

YEAR_DAYS = 365.25


def _jde_to_datetime(jde: float):
    from datetime import datetime
    year, month, day, hour, minute, second = Epoch(jde).get_full_date()
    return datetime(int(year), int(month), int(day), int(hour), int(minute)) + \
        timedelta(seconds=float(second))


def mahadasha_sequence(moon_sidereal_longitude: float, birth_jde: float, cycles: int = 1):
    """
    Return a list of mahadasha periods:
        [{"lord": Graha, "start": datetime, "end": datetime, "years": float}, ...]

    covering `cycles` full 120-year Vimshottari cycles from birth (default
    1 cycle = 120 years, i.e. a full lifetime of coverage).
    """
    idx = nakshatra_index(moon_sidereal_longitude)
    lord = NAKSHATRA_LORDS[idx]

    degrees_into_nakshatra = norm360(moon_sidereal_longitude) % DEG_PER_NAKSHATRA
    fraction_elapsed = degrees_into_nakshatra / DEG_PER_NAKSHATRA
    fraction_remaining = 1.0 - fraction_elapsed

    full_years = VIMSHOTTARI_YEARS[lord]
    first_period_years = full_years * fraction_remaining

    periods = []
    cur_jde = birth_jde
    cur_lord_index = VIMSHOTTARI_ORDER.index(lord)

    # First (partial) mahadasha
    duration_days = first_period_years * YEAR_DAYS
    start_dt = _jde_to_datetime(cur_jde)
    end_jde = cur_jde + duration_days
    end_dt = _jde_to_datetime(end_jde)
    periods.append({"lord": lord, "start": start_dt, "end": end_dt, "years": round(first_period_years, 4)})
    cur_jde = end_jde
    cur_lord_index = (cur_lord_index + 1) % 9

    total_years_covered = first_period_years
    target_years = 120 * cycles

    while total_years_covered < target_years:
        lord = VIMSHOTTARI_ORDER[cur_lord_index]
        years = VIMSHOTTARI_YEARS[lord]
        duration_days = years * YEAR_DAYS
        start_dt = _jde_to_datetime(cur_jde)
        end_jde = cur_jde + duration_days
        end_dt = _jde_to_datetime(end_jde)
        periods.append({"lord": lord, "start": start_dt, "end": end_dt, "years": years})
        cur_jde = end_jde
        cur_lord_index = (cur_lord_index + 1) % 9
        total_years_covered += years

    return periods


def antardasha_sequence(mahadasha_period: dict):
    """
    Given one mahadasha period dict (as returned by mahadasha_sequence),
    return its 9 antardasha sub-periods in the same dict shape.
    """
    lord = mahadasha_period["lord"]
    md_years = mahadasha_period["years"]
    start_jde = Epoch(mahadasha_period["start"].year, mahadasha_period["start"].month,
                       mahadasha_period["start"].day +
                       (mahadasha_period["start"].hour + mahadasha_period["start"].minute / 60
                        + mahadasha_period["start"].second / 3600) / 24.0).jde()

    start_index = VIMSHOTTARI_ORDER.index(lord)
    sub_periods = []
    cur_jde = start_jde
    for i in range(9):
        sub_lord = VIMSHOTTARI_ORDER[(start_index + i) % 9]
        sub_years = md_years * (VIMSHOTTARI_YEARS[sub_lord] / 120.0)
        duration_days = sub_years * YEAR_DAYS
        start_dt = _jde_to_datetime(cur_jde)
        end_jde = cur_jde + duration_days
        end_dt = _jde_to_datetime(end_jde)
        sub_periods.append({
            "lord": sub_lord, "start": start_dt, "end": end_dt,
            "years": round(sub_years, 4),
        })
        cur_jde = end_jde
    return sub_periods
