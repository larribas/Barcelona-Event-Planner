# !/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import clean_string, convert_or_raw, GeolocatedObject
from xml.etree import ElementTree as ET
from HTMLParser import HTMLParser
import urllib2


class BicingProcessor(object):
    """
    Retrieves and processes information about Bicing Stations in Barcelona
    """

    BICING_URL = 'http://wservice.viabicing.cat/v1/getstations.php?v=1'
    HTML_PARSER = HTMLParser()

    def get_stations_near(self, event, mem = {}):
        if 'stations_xml' not in mem:
            # If the stations are not already memorized, we retrieve the XML from the service's URL, and build two lists:
            # One for the stations with >0 available slots; The other for stations with >0 available bikes
            mem['stations_xml'] = ET.fromstring(urllib2.urlopen(self.BICING_URL).read()).findall('station')
            for prop in ['slots', 'bikes']:
                mem['with_%s' % prop] = map(lambda s: BicingStation(**BicingProcessor.as_dict(s)), filter(lambda s: int(s.find(prop).text) > 0, mem['stations_xml']))

        # When asked for the stations near some event (a GeolocatedObject), we filter out those stations at a distance
        # greater than 500m from the event, and sort the rest by proximity
        return (
            sorted (
                filter(lambda station: station.is_within(0.5, event),
                    mem['with_%s' % prop]
                ), key=lambda station: station.geo_distance(event)
            ) for prop in ['slots', 'bikes'])

    @staticmethod
    def as_dict(station_xml):
        return {
            "id": int(station_xml.find('id').text),
            "street": clean_string(BicingProcessor.HTML_PARSER.unescape(station_xml.find('street').text)),
            "lat": convert_or_raw(station_xml.find('lat').text, float),
            "lon": convert_or_raw(station_xml.find('long').text, float),
            "slots": convert_or_raw(station_xml.find('slots').text, int),
            "bikes": convert_or_raw(station_xml.find('bikes').text, int)
        }

class BicingStation(GeolocatedObject):

    def __init__(self, id, street, lat, lon, slots, bikes):
        self.id = id
        self.street = street
        self.lat = lat
        self.lon = lon
        self.slots = slots
        self.bikes = bikes

    def __str__(self):
        return "%s (%s)" % (self.street, self.id)


