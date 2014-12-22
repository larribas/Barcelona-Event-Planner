# !/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import clean_string, convert_or_raw, GeolocatedObject
from xml.etree import ElementTree as ET
import urllib2
import time


class EventProcessor(object):
    """
    Retrieves and processes information about Events taking place in Barcelona in the next 1-2 days
    """

    EVENT_SERVICE_URL = 'http://w10.bcn.es/APPS/asiasiacache/peticioXmlAsia?id=199'

    def __init__(self):
        raw_events = ET.fromstring(urllib2.urlopen(self.EVENT_SERVICE_URL).read()).findall('body/resultat/actes/acte')
        self.events = map(lambda e: Event(**EventProcessor.as_dict(e)), raw_events)

    def get_events(self, query):
        return filter(lambda event: event.complies_with(query), self.events)

    @staticmethod
    def as_dict(event_xml):
        a = event_xml.find('lloc_simple/adreca_simple')
        coord = event_xml.find('lloc_simple/adreca_simple/coordenades/googleMaps')
        return {
            "name": clean_string(event_xml.find('nom').text),
            "place": clean_string(event_xml.find('lloc_simple/nom').text),
            "address": clean_string("%s, %s %s (%s)" % (a.find('carrer').text, a.find('numero').text, a.find('codi_postal').text, a.find('municipi').text)),
            "neighborhood": clean_string(a.find('barri').text),
            "date": convert_or_raw(event_xml.find('data/data_proper_acte').text.split()[0], time.strptime, "%d/%m/%Y"),
            "starts_at": convert_or_raw(event_xml.find('data/data_proper_acte').text.split()[1], time.strptime, "%H.%M"),
            "ends_at": convert_or_raw(event_xml.find('data/hora_fi').text, time.strptime, "%H.%M"),
            "lat": convert_or_raw(coord.get('lat'), float),
            "lon": convert_or_raw(coord.get('lon'), float)
        }


class Event(GeolocatedObject):

    # Determine the allowed query params, and the actual name of the attribute they correspond to
    ALLOWED_Q = {
        'nom': 'name',
        'lloc': 'place',
        'barri': 'neighborhood'
    }

    def __init__(self, name, place, neighborhood, address, date, starts_at, ends_at, lat, lon):
        self.name = name
        self.place = place
        self.address = address
        self.date = date
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.lat = lat
        self.lon = lon
        
    def complies_with(self, query):
        """ Returns true if the event complies with all of the query's requirements. False otherwise """
        return not any([x not in getattr(self, attr) for q,attr in self.ALLOWED_Q.items() if q in query for x in query[q]])

    def __str(self):
        return "%s, at %s on %s" % (self.name, self.place, time.strftime("%d-%m-%y", self.date))