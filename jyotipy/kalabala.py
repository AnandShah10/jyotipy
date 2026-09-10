"""
Kala Bala (temporal strength): BPHS lists 6 sub-components. This module
implements the 4 with clean, directly-quotable BPHS formulas:

  - Nathonnata Bala (day/night strength)
  - Paksha Bala (lunar fortnight strength)
  - Tribhaga Bala (day/night-third strength)
  - Ayana Bala (declination strength)

All four formulas below are transcribed from a direct BPHS 27
translation (bphs.blogspot.com), cross-checked against 2-4 independent
secondary sources each, with zero discrepancies found on the formulas
themselves (only on auxiliary claims not needed here, like whether Sun's
Ayana Bala gets "doubled" -- see the note in shadbala.py's Chesta Bala
section for how that's actually resolved).

NOT IMPLEMENTED, and deliberately left out of this module rather than
guessed:
  - Yuddha Bala (planetary war) -- a correction applied only when two
    "Tara Graha" are within 1 deg of each other (rare). Its magnitude
    formula needs each planet's angular disc diameter, which was only
    found from a single secondary source (not independently confirmed),
    and it has a circular dependency on the very Kala Bala total being
    computed. Skipped rather than built on a single unconfirmed number.

VARSHA/MASA/DINA/HORA BALA -- now implemented, added after the initial
pass above. Point values (15/30/45/60 Virupas respectively) are a direct
BPHS quote. The 4 lords are found via:
  - Dina (day) lord: the weekday ruling planet of the birth day, using a
    SUNRISE-to-SUNRISE civil day boundary (the classical Hindu
    convention), not midnight-to-midnight -- a birth before sunrise
    belongs to the PREVIOUS weekday.
  - Varsha (year) lord: the weekday lord of the day the SIDEREAL Sun most
    recently crossed 0 deg Aries (Mesha Sankranti), found via numerical
    root-finding on the ephemeris.
  - Masa (month) lord: the weekday lord of the day the sidereal Sun most
    recently entered ANY sign (the most recent solar ingress before
    birth), same root-finding approach.
  - Hora (planetary hour) lord: the sunrise-to-next-sunrise period is
    divided into 24 equal parts; the first part is ruled by the day's
    own weekday lord, and subsequent parts cycle through the standard
    Chaldean order (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon,
    repeating) -- this exact cycle is also the historical origin of the
    weekday order itself, cross-checked against the standard planetary-
    hour convention used in both Hindu and Western horary astrology.

A note on "local midnight"/"local noon" throughout: this module uses
LOCAL CLOCK TIME (the birth datetime + UTC offset already on hand), not
true local apparent solar time (which would additionally correct for
the equation of time, typically a +/-15 minute effect). This is a
documented simplification, not an oversight -- the classical formulas
are themselves defined in Ghatis relative to apparent solar midnight,
and a fully rigorous implementation would need equation-of-time
correction. The error this introduces is small relative to the 12-hour
scale these formulas operate on.
"""

import math
from datetime import datetime, timedelta

from .constants import Graha
from .utils import norm360
from pymeeus.Sun import Sun as _MeeusSun

OBLIQUITY_DEG = 23.4393  # mean obliquity of the ecliptic, standard modern value

# -- Nathonnata Bala ----------------------------------------------------

NOON_STRONG = {Graha.SUN, Graha.JUPITER, Graha.VENUS}
MIDNIGHT_STRONG = {Graha.MOON, Graha.MARS, Graha.SATURN}


def nathonnata_bala(planet: Graha, birth_dt: datetime) -> float:
    """
    Day/night strength, 0-60 Virupas. Mercury always gets 60. Sun,
    Jupiter, Venus peak at local noon; Moon, Mars, Saturn peak at local
    midnight; both fall to 0 at the opposite point, linearly.
    """
    if planet == Graha.MERCURY:
        return 60.0
    if planet not in NOON_STRONG and planet not in MIDNIGHT_STRONG:
        return 0.0  # Rahu/Ketu not covered by this classical bala

    hour_decimal = birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
    # Distance from the nearest local midnight (0 at midnight, 12 at noon).
    distance_from_midnight = min(hour_decimal, 24.0 - hour_decimal)

    unnata_bala = (distance_from_midnight / 12.0) * 60.0  # peaks at noon
    if planet in NOON_STRONG:
        return unnata_bala
    return 60.0 - unnata_bala  # midnight-strong planets get the complement


# -- Paksha Bala ----------------------------------------------------------

PAKSHA_BENEFICS = {Graha.MOON, Graha.MERCURY, Graha.JUPITER, Graha.VENUS}
PAKSHA_MALEFICS = {Graha.SUN, Graha.MARS, Graha.SATURN}


def _moon_sun_elongation_folded(moon_tropical: float, sun_tropical: float) -> float:
    """(Moon - Sun), folded to 0-180 -- BPHS: 'if sum exceeds 6 rashis,
    deduct from 12 rashis' i.e. fold anything past 180 back from 360."""
    diff = norm360(moon_tropical - sun_tropical)
    return 360.0 - diff if diff > 180.0 else diff


def paksha_bala(planet: Graha, moon_tropical: float, sun_tropical: float) -> float:
    """
    Lunar fortnight strength, 0-60 Virupas. Benefics (Moon, Mercury,
    Jupiter, Venus) score elongation/3; malefics (Sun, Mars, Saturn)
    score the complement (60 - that). Mercury is treated as an
    unconditional benefic here specifically for this classical rule
    (its usual conditional benefic/malefic status elsewhere in Jyotish
    doesn't apply to this particular BPHS formula).
    """
    if planet not in PAKSHA_BENEFICS and planet not in PAKSHA_MALEFICS:
        return 0.0  # Rahu/Ketu not covered

    elongation = _moon_sun_elongation_folded(moon_tropical, sun_tropical)
    benefic_value = elongation / 3.0
    if planet in PAKSHA_BENEFICS:
        return benefic_value
    return 60.0 - benefic_value


# -- Tribhaga Bala --------------------------------------------------------

# Day divided sunrise-to-sunset into 3 equal parts; night sunset-to-sunrise
# into 3 equal parts. Each third has exactly one ruling planet who scores
# the full 60; everyone else in that third scores 0. Jupiter is the sole
# exception, scoring 60 unconditionally at all times -- BPHS explicitly:
# "Jupiter gets this Bala at all times."
TRIBHAGA_DAY_THIRDS = [Graha.MERCURY, Graha.SUN, Graha.SATURN]
TRIBHAGA_NIGHT_THIRDS = [Graha.MOON, Graha.VENUS, Graha.MARS]


def tribhaga_bala(planet: Graha, is_daytime: bool, third_index: int) -> float:
    """
    third_index: 0, 1, or 2 -- which third of the day (if is_daytime) or
    night (if not) the birth falls into. Jupiter always scores 60
    regardless of the other two arguments (BPHS: "Jupiter gets this Bala
    at all times").
    """
    if planet == Graha.JUPITER:
        return 60.0
    ruling_list = TRIBHAGA_DAY_THIRDS if is_daytime else TRIBHAGA_NIGHT_THIRDS
    if 0 <= third_index <= 2 and ruling_list[third_index] == planet:
        return 60.0
    return 0.0


def _tribhaga_third_index(fraction_elapsed: float) -> int:
    """fraction_elapsed: 0.0 at the start of the day/night period, 1.0 at
    the end. Returns which third (0, 1, 2) it falls into."""
    return min(int(fraction_elapsed * 3), 2)


def sunrise_sunset(dt, utc_offset_hours: float, latitude_deg: float, longitude_deg: float):
    """
    Sunrise and sunset (as naive local-time datetimes, using the same
    utc_offset_hours convention as the rest of this package) for the
    civil date of `dt`. Delegates to pymeeus's Epoch.rise_set, which
    implements the standard Sunrise Equation algorithm -- validated in
    this project against its own documented worked example (a Munich
    coordinate/date pair) before use, not taken on faith.

    Not valid inside the Arctic/Antarctic circles (+/- 66d33') -- pymeeus
    raises ValueError there, which this function lets propagate rather
    than silently returning a wrong time.
    """
    from pymeeus.Epoch import Epoch
    from pymeeus.Angle import Angle
    from datetime import timedelta

    epoch = Epoch(dt.year, dt.month, dt.day)
    lat_angle = Angle(latitude_deg)
    lon_angle = Angle(longitude_deg)  # pymeeus convention: positive East, matching this package's

    rising, setting = epoch.rise_set(lat_angle, lon_angle)

    def _epoch_to_local_dt(e):
        y, m, d, h, mi, s = e.get_full_date()
        utc_dt = datetime(int(y), int(m), int(d), int(h), int(mi)) + timedelta(seconds=float(s))
        return utc_dt + timedelta(hours=utc_offset_hours)

    return _epoch_to_local_dt(rising), _epoch_to_local_dt(setting)


def tribhaga_third_from_time(birth_dt: datetime, period_start: datetime, period_end: datetime, is_daytime: bool):
    """
    Returns (is_daytime, third_index) given the birth moment and the
    boundaries of whichever single period it falls in:
      - is_daytime=True: period_start/end = that day's sunrise/sunset
      - is_daytime=False: period_start/end = the sunset/sunrise
        bracketing the birth moment (whichever calendar days those
        actually fall on -- the caller resolves that, this function just
        divides whatever period it's given into thirds).
    """
    total = (period_end - period_start).total_seconds()
    elapsed = (birth_dt - period_start).total_seconds()
    fraction = max(0.0, min(1.0, elapsed / total)) if total > 0 else 0.0
    return is_daytime, _tribhaga_third_index(fraction)


# -- Ayana Bala -------------------------------------------------------------

# Sign convention per BPHS 27.15-17, cross-checked against 2 independent
# primary-adjacent sources with zero discrepancy.
AYANA_PLUS_ON_NORTH = {Graha.SUN, Graha.MARS, Graha.JUPITER, Graha.VENUS}
AYANA_PLUS_ON_SOUTH = {Graha.MOON, Graha.SATURN}
# Mercury: always plus, regardless of hemisphere.


def declination(tropical_longitude: float) -> float:
    """Approximate declination (Kranti) from ecliptic longitude alone,
    ignoring the planet's own (usually small) ecliptic latitude -- this
    matches the classical formula's own scope, which is explicitly
    longitude-based ('Bhuja is the distance from the nearest Equinoctial
    point'), not a full 3D declination."""
    lon_rad = math.radians(tropical_longitude)
    obliquity_rad = math.radians(OBLIQUITY_DEG)
    return math.degrees(math.asin(math.sin(lon_rad) * math.sin(obliquity_rad)))


def ayana_bala(planet: Graha, tropical_longitude: float) -> float:
    """
    Declination strength, 0-60 Virupas. Formula (BPHS 27, cross-checked
    against 4 independent sources with exact agreement):
    60 * (23.45 +/- Kranti) / 46.9
    """
    if planet == Graha.RAHU or planet == Graha.KETU:
        return 0.0  # not covered by this classical bala

    kranti = declination(tropical_longitude)

    if planet == Graha.MERCURY:
        signed_kranti = abs(kranti)  # always plus, regardless of hemisphere
    elif planet in AYANA_PLUS_ON_NORTH:
        signed_kranti = kranti       # already +north/-south -- no flip needed
    else:  # AYANA_PLUS_ON_SOUTH (Moon, Saturn)
        signed_kranti = -kranti      # flip so southern (negative kranti) becomes positive

    value = 60.0 * (OBLIQUITY_DEG + signed_kranti) / (2 * OBLIQUITY_DEG)
    return max(0.0, min(60.0, value))


def resolve_day_night_period(birth_dt: datetime, utc_offset_hours: float,
                              latitude_deg: float, longitude_deg: float):
    """
    Figures out whether birth_dt falls in daytime or nighttime, and
    returns (is_daytime, period_start, period_end) for whichever single
    sunrise-to-sunset or sunset-to-sunrise window actually contains it --
    resolving the "which calendar day's sunrise/sunset" ambiguity so
    tribhaga_third_from_time() never has to guess.
    """
    today_sunrise, today_sunset = sunrise_sunset(birth_dt, utc_offset_hours, latitude_deg, longitude_deg)

    if today_sunrise <= birth_dt < today_sunset:
        return True, today_sunrise, today_sunset

    if birth_dt < today_sunrise:
        yesterday = birth_dt - timedelta(days=1)
        _, yesterday_sunset = sunrise_sunset(yesterday, utc_offset_hours, latitude_deg, longitude_deg)
        return False, yesterday_sunset, today_sunrise

    tomorrow = birth_dt + timedelta(days=1)
    tomorrow_sunrise, _ = sunrise_sunset(tomorrow, utc_offset_hours, latitude_deg, longitude_deg)
    return False, today_sunset, tomorrow_sunrise


# -- Varsha / Masa / Dina / Hora Bala -----------------------------------

VARSHA_MASA_DINA_HORA_POINTS = {"varsha": 15.0, "masa": 30.0, "dina": 45.0, "hora": 60.0}

# Standard weekday -> ruling planet (Python's datetime.weekday(): Monday=0).
WEEKDAY_LORDS = {
    0: Graha.MOON,      # Monday
    1: Graha.MARS,      # Tuesday
    2: Graha.MERCURY,   # Wednesday
    3: Graha.JUPITER,   # Thursday
    4: Graha.VENUS,     # Friday
    5: Graha.SATURN,    # Saturday
    6: Graha.SUN,       # Sunday
}

# Chaldean order, used for both the historical weekday sequence and the
# hour-to-hour cycle within a single sunrise-to-sunrise day.
CHALDEAN_ORDER = [Graha.SATURN, Graha.JUPITER, Graha.MARS, Graha.SUN,
                  Graha.VENUS, Graha.MERCURY, Graha.MOON]


def _sidereal_sun_longitude(dt: datetime, utc_offset_hours: float, ayanamsa) -> float:
    from . import ephemeris as ephemeris_mod
    from .ayanamsa import tropical_to_sidereal
    epoch = ephemeris_mod.epoch_from_datetime(dt, utc_offset_hours)
    tropical = ephemeris_mod.tropical_longitudes(epoch)
    return tropical_to_sidereal(tropical[Graha.SUN], epoch, ayanamsa)


def find_most_recent_solar_ingress(before_dt: datetime, utc_offset_hours: float,
                                    target_sidereal_degree: float, ayanamsa,
                                    max_iterations: int = 20) -> datetime:
    """
    Finds the most recent moment before `before_dt` at which the sidereal
    Sun's longitude equals `target_sidereal_degree` (mod 360), via
    Newton-style iteration using the Sun's near-constant ~0.9856 deg/day
    mean motion. Converges in a handful of iterations since the Sun's
    actual speed varies only ~+/-1.7% around that mean.
    """
    MEAN_DAILY_MOTION = 360.0 / 365.2422  # ~0.9856 deg/day

    guess = before_dt
    for _ in range(max_iterations):
        current = _sidereal_sun_longitude(guess, utc_offset_hours, ayanamsa)
        # How far PAST the target has the Sun already moved (0-360, since
        # we're looking for the most recent past crossing)?
        degrees_past_target = norm360(current - target_sidereal_degree)
        if degrees_past_target < 1e-6 or degrees_past_target > 360 - 1e-6:
            break
        days_back = degrees_past_target / MEAN_DAILY_MOTION
        new_guess = guess - timedelta(days=days_back)
        if abs((new_guess - guess).total_seconds()) < 1.0:  # converged to within 1 second
            guess = new_guess
            break
        guess = new_guess
    return guess


def _civil_weekday(dt: datetime, sunrise_today: datetime) -> int:
    """Python weekday() (Monday=0) for the SUNRISE-based civil day
    containing dt -- if dt is before that day's sunrise, it still
    belongs to the PREVIOUS weekday."""
    if dt < sunrise_today:
        return (dt - timedelta(days=1)).weekday()
    return dt.weekday()


def dina_bala(planet: Graha, birth_dt: datetime, utc_offset_hours: float,
              latitude: float, longitude: float) -> float:
    """Day lord strength: 45 Virupas if `planet` rules the sunrise-based
    civil weekday of birth, else 0."""
    sunrise_today, _ = sunrise_sunset(birth_dt, utc_offset_hours, latitude, longitude)
    weekday = _civil_weekday(birth_dt, sunrise_today)
    return VARSHA_MASA_DINA_HORA_POINTS["dina"] if WEEKDAY_LORDS[weekday] == planet else 0.0


def varsha_bala(planet: Graha, birth_dt: datetime, utc_offset_hours: float,
                 latitude: float, longitude: float, ayanamsa) -> float:
    """Year lord strength: 15 Virupas if `planet` rules the weekday on
    which the sidereal Sun most recently entered Aries (Mesha Sankranti)."""
    ingress_dt = find_most_recent_solar_ingress(birth_dt, utc_offset_hours, 0.0, ayanamsa)
    sunrise_that_day, _ = sunrise_sunset(ingress_dt, utc_offset_hours, latitude, longitude)
    weekday = _civil_weekday(ingress_dt, sunrise_that_day)
    return VARSHA_MASA_DINA_HORA_POINTS["varsha"] if WEEKDAY_LORDS[weekday] == planet else 0.0


def masa_bala(planet: Graha, birth_dt: datetime, utc_offset_hours: float,
               latitude: float, longitude: float, ayanamsa) -> float:
    """Month lord strength: 30 Virupas if `planet` rules the weekday on
    which the sidereal Sun most recently entered its current sign."""
    current_sun_sidereal = _sidereal_sun_longitude(birth_dt, utc_offset_hours, ayanamsa)
    current_sign_start = (int(current_sun_sidereal // 30)) * 30.0
    ingress_dt = find_most_recent_solar_ingress(birth_dt, utc_offset_hours, current_sign_start, ayanamsa)
    sunrise_that_day, _ = sunrise_sunset(ingress_dt, utc_offset_hours, latitude, longitude)
    weekday = _civil_weekday(ingress_dt, sunrise_that_day)
    return VARSHA_MASA_DINA_HORA_POINTS["masa"] if WEEKDAY_LORDS[weekday] == planet else 0.0


def hora_lord(birth_dt: datetime, utc_offset_hours: float, latitude: float, longitude: float) -> Graha:
    """
    The ruling planet of the specific 1/24th part of the sunrise-to-
    next-sunrise period containing birth_dt. The civil day boundary is
    sunrise-based (same convention as _civil_weekday): a birth before
    today's sunrise belongs to yesterday's sunrise-to-sunrise cycle.
    """
    today_sunrise, _ = sunrise_sunset(birth_dt, utc_offset_hours, latitude, longitude)
    if birth_dt < today_sunrise:
        day_start_sunrise, _ = sunrise_sunset(birth_dt - timedelta(days=1), utc_offset_hours, latitude, longitude)
    else:
        day_start_sunrise = today_sunrise
    next_day_sunrise, _ = sunrise_sunset(day_start_sunrise + timedelta(days=1), utc_offset_hours, latitude, longitude)

    total_seconds = (next_day_sunrise - day_start_sunrise).total_seconds()
    hora_length = total_seconds / 24.0
    elapsed = (birth_dt - day_start_sunrise).total_seconds()
    hora_index = min(int(elapsed // hora_length), 23)

    weekday = _civil_weekday(birth_dt, day_start_sunrise)
    first_hora_lord = WEEKDAY_LORDS[weekday]
    start_pos = CHALDEAN_ORDER.index(first_hora_lord)
    return CHALDEAN_ORDER[(start_pos + hora_index) % 7]


def hora_bala(planet: Graha, birth_dt: datetime, utc_offset_hours: float,
              latitude: float, longitude: float) -> float:
    """Hour lord strength: 60 Virupas if `planet` rules the specific
    planetary hour (Hora) containing the birth moment."""
    return VARSHA_MASA_DINA_HORA_POINTS["hora"] if hora_lord(
        birth_dt, utc_offset_hours, latitude, longitude) == planet else 0.0


def varsha_masa_dina_hora_bala(planet: Graha, birth_dt: datetime, utc_offset_hours: float,
                                latitude: float, longitude: float, ayanamsa) -> dict:
    """All 4 sub-scores plus their sum (max 150 Virupas, scored only
    when `planet` happens to rule one or more of the 4 lordships)."""
    components = {
        "varsha_bala": varsha_bala(planet, birth_dt, utc_offset_hours, latitude, longitude, ayanamsa),
        "masa_bala": masa_bala(planet, birth_dt, utc_offset_hours, latitude, longitude, ayanamsa),
        "dina_bala": dina_bala(planet, birth_dt, utc_offset_hours, latitude, longitude),
        "hora_bala": hora_bala(planet, birth_dt, utc_offset_hours, latitude, longitude),
    }
    components["total"] = sum(components.values())
    return components


# -- Chesta Bala for the 5 non-luminary planets --------------------------

_MEAN_LONGITUDE_CLASSES = {}


def _get_mean_longitude_class(planet: Graha):
    global _MEAN_LONGITUDE_CLASSES
    if not _MEAN_LONGITUDE_CLASSES:
        from pymeeus.Mercury import Mercury
        from pymeeus.Venus import Venus
        from pymeeus.Mars import Mars
        from pymeeus.Jupiter import Jupiter
        from pymeeus.Saturn import Saturn
        _MEAN_LONGITUDE_CLASSES = {
            Graha.MERCURY: Mercury, Graha.VENUS: Venus, Graha.MARS: Mars,
            Graha.JUPITER: Jupiter, Graha.SATURN: Saturn,
        }
    return _MEAN_LONGITUDE_CLASSES[planet]


def chesta_bala_non_luminary(planet: Graha, epoch, planet_true_tropical_longitude: float) -> float:
    """
    Motional strength for the 5 non-luminary planets, 0-60 Virupas.

    Formula (cross-confirmed by 3 independent sources -- an academic
    paper on classical Indian astronomical methods giving the cleanest
    statement, "Chesta Bala = 0.33 * (Sighrocca - average geocentric
    longitude)", plus 2 modern astrology sites independently describing
    the same mean-longitude/true-longitude-average structure):

        Chesta Kendra = Sun's mean longitude
                         - (planet's mean longitude + planet's true
                            tropical longitude) / 2
        (folded to 0-180, same fold pattern as Uchcha/Dig/Ayana Bala)
        Chesta Bala = Chesta Kendra / 3

    This naturally peaks (60) near opposition -- when superior planets
    are typically retrograde -- and bottoms out (0) near conjunction
    with the Sun (combustion), matching the classical claim that
    retrograde planets score highest without needing a separate
    explicit retrograde check bolted on.

    "Mean longitude" here is pymeeus's standard modern orbital-element
    mean longitude (validated against pymeeus's own documented worked
    example for Mars before use), not a reconstruction of ancient
    Siddhantic mean-motion tables -- these are extremely close in
    practice (both describe the same underlying near-circular orbit),
    and using the well-validated modern figure avoids a second,
    separate sourcing project for classical mean-motion constants.
    """
    from pymeeus.Earth import Earth

    earth_mean_lon, _, _, _, _, _ = Earth.orbital_elements_mean_equinox(epoch)
    sun_mean_longitude = norm360(float(earth_mean_lon) + 180.0)

    planet_class = _get_mean_longitude_class(planet)
    planet_mean_lon, _, _, _, _, _ = planet_class.orbital_elements_mean_equinox(epoch)
    planet_mean_lon = norm360(float(planet_mean_lon))

    # Circular average of mean and true longitude -- naive (a+b)/2 breaks
    # near the 0/360 boundary (e.g. averaging 355 and 5 should give 0,
    # not 180). Adjust one value by +/-360 if they're on opposite sides
    # of the wraparound before averaging.
    true_lon = planet_true_tropical_longitude
    if abs(planet_mean_lon - true_lon) > 180.0:
        if planet_mean_lon > true_lon:
            true_lon += 360.0
        else:
            planet_mean_lon += 360.0
    average_geocentric = norm360((planet_mean_lon + true_lon) / 2.0)

    chesta_kendra_raw = norm360(sun_mean_longitude - average_geocentric)
    chesta_kendra = 360.0 - chesta_kendra_raw if chesta_kendra_raw > 180.0 else chesta_kendra_raw

    return chesta_kendra / 3.0