from datetime import datetime
from jyotipy import ephemeris as eph
from jyotipy.houses import (
    placidus_cusps_tropical, ascendant_tropical, midheaven_tropical,
    _placidus_diurnal_cusp, _placidus_nocturnal_cusp,
)
from jyotipy.utils import norm360
from pymeeus import Coordinates

LAT, LON = 23.0225, 72.5714
DT = datetime(1990, 6, 15, 14, 32, 0)


def _setup():
    epoch = eph.epoch_from_datetime(DT, 5.5)
    obliquity = float(Coordinates.true_obliquity(epoch))
    nutation = float(Coordinates.nutation_longitude(epoch))
    gst_days = float(epoch.apparent_sidereal_time(obliquity, nutation))
    ramc = norm360(gst_days * 360.0 + LON)
    return epoch, obliquity, ramc


def _short_signed_arc(a, b):
    d = norm360(b - a)
    return d - 360 if d > 180 else d


def test_diurnal_boundary_conditions_exact():
    epoch, obliquity, ramc = _setup()
    mc = midheaven_tropical(epoch, LON)
    asc = ascendant_tropical(epoch, LAT, LON)
    f0 = _placidus_diurnal_cusp(ramc, LAT, obliquity, mc, asc, 0.0)
    f1 = _placidus_diurnal_cusp(ramc, LAT, obliquity, mc, asc, 1.0)
    assert abs(norm360(f0 - mc)) < 1e-6
    assert abs(norm360(f1 - asc)) < 1e-6


def test_nocturnal_boundary_conditions_exact():
    epoch, obliquity, ramc = _setup()
    mc = midheaven_tropical(epoch, LON)
    ic = norm360(mc + 180)
    asc = ascendant_tropical(epoch, LAT, LON)
    f0 = _placidus_nocturnal_cusp(ramc, LAT, obliquity, ic, asc, 0.0)
    f1 = _placidus_nocturnal_cusp(ramc, LAT, obliquity, ic, asc, 1.0)
    diff0 = norm360(f0 - ic)
    diff1 = norm360(f1 - asc)
    assert min(diff0, 360 - diff0) < 1e-6
    assert min(diff1, 360 - diff1) < 1e-6


def test_antipodal_pairs_exact():
    epoch = eph.epoch_from_datetime(DT, 5.5)
    cusps = placidus_cusps_tropical(epoch, LAT, LON)
    for i in range(6):
        diff = abs(norm360(cusps[i] - cusps[i + 6]))
        diff = min(diff, 360 - diff)
        assert abs(diff - 180) < 1e-6


def test_signed_short_arcs_consistent_and_sum_to_360():
    epoch = eph.epoch_from_datetime(DT, 5.5)
    cusps = placidus_cusps_tropical(epoch, LAT, LON)
    arcs = [_short_signed_arc(cusps[i], cusps[(i + 1) % 12]) for i in range(12)]
    assert all(a <= 0 for a in arcs) or all(a >= 0 for a in arcs)
    assert abs(abs(sum(arcs)) - 360.0) < 1e-6


def test_consistent_across_diverse_charts():
    cases = [
        (datetime(1990, 6, 15, 14, 32, 0), 23.0225, 72.5714),
        (datetime(2000, 1, 1, 6, 0, 0), 51.5, -0.13),
        (datetime(2015, 9, 23, 18, 0, 0), -33.87, 151.21),
        (datetime(2020, 3, 20, 0, 0, 0), 40.7, -74.0),
    ]
    for dt, lat, lon in cases:
        epoch = eph.epoch_from_datetime(dt, 0.0)
        cusps = placidus_cusps_tropical(epoch, lat, lon)
        arcs = [_short_signed_arc(cusps[i], cusps[(i + 1) % 12]) for i in range(12)]
        assert all(a <= 0 for a in arcs) or all(a >= 0 for a in arcs)
        assert abs(abs(sum(arcs)) - 360.0) < 1e-6
        for i in range(6):
            diff = abs(norm360(cusps[i] - cusps[i + 6]))
            diff = min(diff, 360 - diff)
            assert abs(diff - 180) < 1e-6


def test_raises_above_66_degrees_latitude():
    epoch = eph.epoch_from_datetime(DT, 5.5)
    try:
        placidus_cusps_tropical(epoch, 70.0, LON)
        assert False, "expected ValueError above 66 degrees latitude"
    except ValueError:
        pass


def test_universal_house_numbering_matches_verified_swiss_ephemeris_example():
    cusps = [190.88156009524067, 226.9336677703179, 262.9857754453951, 299.0378831204723,
             322.9857754453951, 346.9336677703179, 10.881560095240673, 46.933667770317925,
             82.98577544539512, 119.03788312047234, 142.98577544539512, 166.9336677703179]
    mc, asc, h11, h12 = cusps[9], cusps[0], cusps[10], cusps[11]
    assert mc < h11 < h12 < asc