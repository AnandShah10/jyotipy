"""
Panchanga: the 5 daily almanac elements -- Tithi, Vara, Nakshatra, Yoga
(Nitya Yoga), Karana. All are defined by angular relationships between
the Sun and Moon, which are ayanamsa-INDEPENDENT (a constant offset
applied to both bodies cancels out in the difference/sum), except
Nakshatra, which needs the sidereal Moon longitude specifically since
nakshatra boundaries are fixed relative to the sidereal zodiac.

Tithi names, the 27 Nitya Yoga names (in order), and the Karana algorithm
below are cross-checked against multiple independent public references
(the Nitya Yoga list against 3+ independent listings; the Karana
assignment algorithm against its Wikipedia formalization, which gives an
unambiguous K=0..59 -> name mapping).
"""

from .utils import norm360
from .nakshatra import nakshatra_info

TITHI_NAMES_SHUKLA = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
]
TITHI_NAMES_KRISHNA = TITHI_NAMES_SHUKLA[:-1] + ["Amavasya"]

NITYA_YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
    "Vaidhriti",
]

VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

_MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]


def tithi_info(sun_longitude: float, moon_longitude: float) -> dict:
    """Tithi from Sun/Moon longitudes (tropical or sidereal -- doesn't
    matter, the difference cancels ayanamsa)."""
    elongation = norm360(moon_longitude - sun_longitude)
    tithi_num = int(elongation // 12) + 1  # 1..30
    if tithi_num <= 15:
        paksha = "Shukla"
        name = TITHI_NAMES_SHUKLA[tithi_num - 1]
    else:
        paksha = "Krishna"
        name = TITHI_NAMES_KRISHNA[tithi_num - 16]
    degrees_into_tithi = elongation % 12
    return {"number": tithi_num, "paksha": paksha, "name": name,
            "degrees_into_tithi": round(degrees_into_tithi, 4)}


def nitya_yoga_info(sun_longitude: float, moon_longitude: float) -> dict:
    total = norm360(sun_longitude + moon_longitude)
    idx = int(total // (360.0 / 27.0))
    return {"name": NITYA_YOGA_NAMES[idx], "index": idx}


def karana_info(sun_longitude: float, moon_longitude: float) -> dict:
    """
    Per the standard algorithm: D = (Moon - Sun) mod 360, K = floor(D/6),
    K in [0,59]. K=0 -> Kimstughna, K=1..56 -> the 7 movable karanas
    cycling 8x, K=57/58/59 -> Shakuni/Chatushpada/Naga.
    """
    d = norm360(moon_longitude - sun_longitude)
    k = int(d // 6)  # 0..59
    if k == 0:
        name = "Kimstughna"
    elif 1 <= k <= 56:
        name = _MOVABLE_KARANAS[(k - 1) % 7]
    elif k == 57:
        name = "Shakuni"
    elif k == 58:
        name = "Chatushpada"
    else:  # k == 59
        name = "Naga"
    return {"name": name, "k": k}


def vara_info(weekday_index: int) -> str:
    """weekday_index: Python's datetime.weekday() convention won't match
    directly -- pass in datetime.isoweekday() % 7 (0=Sunday) or use
    vara_from_datetime() below instead."""
    return VARA_NAMES[weekday_index % 7]


def vara_from_datetime(dt) -> str:
    # Python: Monday=0 ... Sunday=6. We want Sunday=0 ... Saturday=6.
    return VARA_NAMES[(dt.weekday() + 1) % 7]


def full_panchanga(sun_tropical: float, moon_tropical: float,
                    moon_sidereal: float, dt) -> dict:
    """Convenience: compute all 5 angas at once."""
    return {
        "tithi": tithi_info(sun_tropical, moon_tropical),
        "nakshatra": nakshatra_info(moon_sidereal),
        "yoga": nitya_yoga_info(sun_tropical, moon_tropical),
        "karana": karana_info(sun_tropical, moon_tropical),
        "vara": vara_from_datetime(dt),
    }
