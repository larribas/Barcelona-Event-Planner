# !/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sin, cos, sqrt, atan2, radians
import unicodedata

def clean_string(input_string):
    """ Returns the string without leading or trailing whitespace, without accents, and lowercased """
    input_string = input_string if isinstance(input_string, unicode) else unicode(input_string, 'utf-8')
    return unicodedata.normalize('NFKD', input_string.strip().lower()).encode('ASCII', 'ignore')

def convert_or_raw(raw, func, *args):
    """ For those pieces of data that may or may not have the appropriate format/value, tries to convert them, or returns them unchanged """
    try:
        return func(raw, *args)
    except:
        return raw


class GeolocatedObject(object):

    def is_within(self, radius, another):
        return self.geo_distance(another) < radius

    def geo_distance(self, another):
        lat1, lon1, lat2, lon2 = radians(self.lat), radians(self.lon), radians(another.lat), radians(another.lon)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = 6371.0 * c
        return distance


