"""
Small stateless helpers used across the package. Keeping angle math and
datetime handling here means the astronomy/astrology modules only deal
with plain floats (degrees, 0-360) and don't each reinvent normalization.
"""

from datetime import datetime, timezone, timedelta
from pymeeus.Epoch import Epoch


def norm360(deg: float) -> float:
    """Normalize any angle to [0, 360)."""
    result = deg % 360.0
    return result + 360.0 if result < 0 else result


def deg_to_dms(deg: float):
    """Convert decimal degrees to (degrees, minutes, seconds) as ints/float."""
    deg = abs(deg)
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return d, m, round(s, 2)

def deg_to_dms_str(deg: float) -> str:
    d, m, s = deg_to_dms(deg)
    return f"{d}\N{DEGREE SIGN} {m}' {s}\""


def sign_index(longitude: float) -> int:
    """0 = Aries ... 11 = Pisces, given a sidereal longitude in [0, 360)."""
    return int(norm360(longitude) // 30)


def degree_in_sign(longitude: float) -> float:
    """The 0-30 degree position within whatever sign the longitude falls in."""
    return norm360(longitude) % 30


def to_utc_epoch(dt: datetime, utc_offset_hours: float = 0.0) -> Epoch:
    """
    Convert a local civil datetime + UTC offset into a pymeeus Epoch (UT).

    dt: a naive datetime in LOCAL civil time (e.g. birth time as recorded).
    utc_offset_hours: the local zone's offset from UTC, e.g. 5.5 for IST.

    We deliberately take a naive datetime + explicit offset rather than
    requiring a tz-aware datetime, because historical birth records rarely
    come with an IANA tz name attached — just "born in Mumbai, clock said
    14:32". Callers who *do* have tz-aware datetimes should convert to UTC
    themselves and pass utc_offset_hours=0.
    """
    if dt.tzinfo is not None:
        dt_utc = dt.astimezone(timezone.utc)
    else:
        dt_utc = dt - timedelta(hours=utc_offset_hours)

    hour_decimal = (
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )
    return Epoch(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)


def format_dasha_date(epoch_start_year_decimal: float) -> str:
    """Convert a decimal-year epoch (e.g. 1990.6523) to a rough Y-M-D string.
    Used for dasha period boundaries where we work in fractional years."""
    year = int(epoch_start_year_decimal)
    remainder = epoch_start_year_decimal - year
    days_in_year = 365.2425
    day_of_year = remainder * days_in_year
    base = datetime(year, 1, 1) + timedelta(days=day_of_year)
    return base.strftime("%Y-%m-%d")
