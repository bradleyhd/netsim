import math
from geopy import Point
from geopy.distance import VincentyDistance

def calc_bearing(lon1, lat1, lon2, lat2):

    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    rlon1 = math.radians(lon1)
    rlon2 = math.radians(lon2)
    dlon = math.radians(lon2-lon1)

    b = math.atan2(math.sin(dlon)*math.cos(rlat2),math.cos(rlat1)*math.sin(rlat2)-math.sin(rlat1)*math.cos(rlat2)*math.cos(dlon))
    bd = math.degrees(b)
    br, bn = divmod(bd+360,360)

    return bn

def estimate_location(lon1, lat1, lon2, lat2, dist_m):

    #print('--')
    #print('estimating location %f %f -> %f %f at %f km' % (lon1, lat1, lon2, lat2, dist_km))

    bearing = calc_bearing(lon2, lat2, lon1, lat1)
    #print('got bearing %d' % bearing)

    origin = Point(lat2, lon2)
    dest = VincentyDistance(meters=dist_m).destination(origin, bearing)

    #print('estimated location: %f %f' % (dest.longitude, dest.latitude))
    return (dest.longitude, dest.latitude)
    #print('--')
