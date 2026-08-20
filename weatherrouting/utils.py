# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
# Copyright (C) 2012 Riccardo Apolloni
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# For detail about GNU see <http://www.gnu.org/licenses/>.
import math
from typing import Tuple

import latlon

# from geographiclib.geodesic import Geodesic
# geod = Geodesic.WGS84

EARTH_RADIUS = 60.0 * 360 / (2 * math.pi)  # nm
NAUTICAL_MILE_IN_KM = 1.852
# Speed conversion m/s to kt
MS2KT = 1.94384


def ms_to_knots(v: float) -> float:
    return v * MS2KT


def cfbinomiale(n: int, i: int) -> float:
    # TODO: remove
    return math.factorial(n) / (math.factorial(n - i) * math.factorial(i))


def ortodromic2(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> Tuple[float, float]:
    # TODO: remove
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dp2 = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) * math.sin(dp2 / 2) + math.cos(p1) * math.cos(p2) * math.sin(
        dp2 / 2
    ) * math.sin(dp2 / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return (EARTH_RADIUS * c, a)


EARTH_RADIUS_KM = 6371.0088
EARTH_RADIUS_NM = 3440.065
_DEG2RAD = math.pi / 180.0
_RAD2DEG = 180.0 / math.pi


def ortodromic(
    lat_a: float, lon_a: float, lat_b: float, lon_b: float
) -> Tuple[float, float]:
    """Returns the ortodromic distance in km and initial heading in radians between A and B"""
    phi1 = lat_a * _DEG2RAD
    phi2 = lat_b * _DEG2RAD
    dphi = phi2 - phi1
    dlam = (lon_b - lon_a) * _DEG2RAD
    a = math.sin(dphi * 0.5) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam * 0.5) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    dist_km = EARTH_RADIUS_KM * c

    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    hdg = math.atan2(y, x)
    return (dist_km, hdg)


def lossodromic(
    lat_a: float, lon_a: float, lat_b: float, lon_b: float
) -> Tuple[float, float]:
    """Returns the lossodromic (rhumb line) distance in km and heading in radians between A and B"""
    phi1 = lat_a * _DEG2RAD
    phi2 = lat_b * _DEG2RAD
    dphi = phi2 - phi1
    dlam = (lon_b - lon_a) * _DEG2RAD
    
    t1 = math.tan(math.pi * 0.25 + phi1 * 0.5)
    t2 = math.tan(math.pi * 0.25 + phi2 * 0.5)
    dpsi = math.log(max(1e-12, t2 / max(1e-12, t1))) if abs(dphi) > 1e-12 else 0.0
    q = dphi / dpsi if abs(dpsi) > 1e-12 else math.cos(phi1)
    d = math.sqrt(dphi * dphi + q * q * dlam * dlam) * EARTH_RADIUS_KM
    brg = math.atan2(dlam, dpsi)
    return (d, brg)


def km2nm(d: float) -> float:
    return d * 0.539957


def nm2km(d: float) -> float:
    return d / 0.539957


def point_distance(
    lat_a: float, lon_a: float, lat_b: float, lon_b: float, unit: str = "nm"
) -> float:
    """Returns the distance between two geo points (Haversine formula)"""
    phi1 = lat_a * _DEG2RAD
    phi2 = lat_b * _DEG2RAD
    dphi = phi2 - phi1
    dlam = (lon_b - lon_a) * _DEG2RAD
    a = math.sin(dphi * 0.5) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam * 0.5) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    r = EARTH_RADIUS_NM if unit == "nm" else EARTH_RADIUS_KM
    return r * c


def routage_point_distance(
    lat_a: float, lon_a: float, distance: float, hdg: float, unit: str = "nm"
) -> Tuple[float, float]:
    """Returns the destination point from (lat_a, lon_a) given (distance, hdg)"""
    d_nm = distance if unit == "nm" else km2nm(distance)
    d_rad = d_nm / EARTH_RADIUS_NM
    phi1 = lat_a * _DEG2RAD
    lam1 = lon_a * _DEG2RAD
    sin_phi1 = math.sin(phi1)
    cos_phi1 = math.cos(phi1)
    sin_d = math.sin(d_rad)
    cos_d = math.cos(d_rad)
    sin_hdg = math.sin(hdg)
    cos_hdg = math.cos(hdg)

    sin_phi2 = sin_phi1 * cos_d + cos_phi1 * sin_d * cos_hdg
    phi2 = math.asin(max(-1.0, min(1.0, sin_phi2)))
    y = sin_hdg * sin_d * cos_phi1
    x = cos_d - sin_phi1 * sin_phi2
    lam2 = lam1 + math.atan2(y, x)
    return (phi2 * _RAD2DEG, (lam2 * _RAD2DEG + 540.0) % 360.0 - 180.0)


def max_reach_distance(p, speed: float, dt: float = (1.0 / 60.0 * 60.0)) -> float:
    return speed * dt


def reduce360(alfa: float) -> float:
    if math.isnan(alfa):
        return 0.0

    n_ = int(alfa * 0.5 / math.pi)
    n = math.copysign(n_, 1)
    if alfa > 2.0 * math.pi:
        alfa = alfa - n * 2.0 * math.pi
    if alfa < 0:
        alfa = (n + 1) * 2.0 * math.pi + alfa
    if alfa > 2.0 * math.pi or alfa < 0:
        return 0.0
    return alfa


def reduce180(alfa: float) -> float:
    if alfa > math.pi:
        alfa = alfa - 2 * math.pi
    if alfa < -math.pi:
        alfa = 2 * math.pi + alfa
    if alfa > math.pi or alfa < -math.pi:
        return 0.0
    return alfa


def path_as_geojson(path) -> object:
    feats = []
    route = []

    for order, wayp in enumerate(path):
        feat = {
            "type": "Feature",
            "id": order,
            "geometry": {
                "type": "Point",
                "coordinates": [wayp.pos[1], wayp.pos[0]],  # longitude, latitude
            },
            "properties": {
                "timestamp": str(wayp.time),
                "twd": math.degrees(wayp.twd),
                "tws": wayp.tws,
                "knots": wayp.speed,
                "heading": wayp.brg,
            },
        }
        feats.append(feat)
        route.append([wayp.pos[1], wayp.pos[0]])  # longitude, latitude

    feats.append(
        {
            "type": "Feature",
            "id": 999,
            "geometry": {"type": "LineString", "coordinates": route},
            "properties": {
                "start-timestamp": str(path[0].time),
                "end-timestamp": str(path[-1].time),
            },
        }
    )

    return {"type": "FeatureCollection", "features": feats}
