# !/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import convert_or_raw, GeolocatedObject
from os.path import isfile
import csv


class PublicTransportProcessor(object):
    """
    Retrieves and processes information about Public Transportation Stations in Barcelona
    """

    TRAIN_PATH = 'Documents/TRANSPORTS.csv'
    BUS_PATH = 'Documents/ESTACIONS_BUS.csv'

    def __init__(self):
        assert isfile(self.TRAIN_PATH)
        assert isfile(self.BUS_PATH)

    def get_stations_near(self, event, mem = {}):
        if 'stations' not in mem:
            # If the stations are not already memorized, we retrieve the CSV as dictionaries from the proper files, 
            # concatenate bus and train data, and map them onto PublicTransportStation objects
            mem['stations'] = map(
                lambda station: PublicTransportStation(**PublicTransportProcessor.as_dict(station)),
                reduce(
                    lambda x,y: x + y,
                    [list(csv.DictReader(open(path, 'r'), delimiter=';')) for path in [self.TRAIN_PATH, self.BUS_PATH]]
                )
            )

        # When asked for the stations near some event (a GeolocatedObject), we filter out those stations at a distance
        # greater than 1km from the event, remove duplicates (turning the list into a set), and sort them (the closest one first)
        return sorted(
            set(filter(
                lambda station: station.is_within(1.0, event),
                mem['stations']
            )),
            key=lambda station: station.geo_distance(event)
        )

    @staticmethod
    def dehydrate_street(field_type, field):
        if field_type == 'K017': # Estació d'Autobusos Barcelona Fabra i Puig 
            return field[30:]
        elif field_type == 'K004': # Tren AEROPORT- AEROPORT-
            return field[16:-1]
        elif field_type == 'K008': # Estació Marítima TRASMEDITERRÁNEA-
            return field[17:-1]
        elif field_type == 'K009': # Funicular VALLVIDRERA - superior-
            return ''
        elif field_type in ['K015', 'K014', 'K016']: # BUS/NITBUS/AEROBUS -N14-N2-N3--
            return ''
        elif field_type in ['K001', 'K011', 'K002', 'K003', 'K010']: # FGC/TRAMVIA (L8) - MOLÍ NOU-CIUTAT COOPERATIVA-
            return field[field.find('-')+2:-1]
        else:
            return ''

    @staticmethod
    def dehydrate_lines(field_type, field):
        if field_type == 'K017': # Estació d'Autobusos Barcelona Fabra i Puig
            return ['Bus Station']
        elif field_type == 'K004': # Tren AEROPORT- AEROPORT-
            return ['Airport Train']
        elif field_type == 'K008': # Estació Marítima TRASMEDITERRÁNEA-
            return ['Maritime Station']
        elif field_type == 'K009': # Funicular VALLVIDRERA - superior-
            return [field[:-12]]
        elif field_type in ['K015', 'K014', 'K016']: # BUS/NITBUS/AEROBUS -N14-N2-N3--
            return field[field.find('-')+1:-2].split('-')
        elif field_type in ['K001', 'K011']: # FGC/TRAMVIA (L8) - MOLÍ NOU-CIUTAT COOPERATIVA-
            return field[field.find('(')+1:field.find(')')].split(', ')
        elif field_type in ['K002', 'K003', 'K010']: # RENFE/FGC - ST. FELIU DE LLOBREGAT-
            return [field.split()[0]]
        else:
            return []

    @staticmethod
    def as_dict(station_csv):
        return {
            "kind": unicode(station_csv['NOM_CAPA_ANG'], 'ISO-8859-1'),
            "street": PublicTransportProcessor.dehydrate_street(station_csv['CODI_CAPA'], unicode(station_csv['EQUIPAMENT'], 'ISO-8859-1')),
            "lines": PublicTransportProcessor.dehydrate_lines(station_csv['CODI_CAPA'], unicode(station_csv['EQUIPAMENT'], 'ISO-8859-1')),
            "lat": convert_or_raw(station_csv['LATITUD'], float),
            "lon": convert_or_raw(station_csv['LONGITUD'], float)
        }
        

class PublicTransportStation(GeolocatedObject):

    def __init__(self, kind, street, lines, lat, lon):
        self.kind = kind
        self.street = street
        self.lines = lines
        self.lat = lat
        self.lon = lon

    # Eq and Hash magic methods are necessary to implement the removal of duplicates (which is done transforming the collection into a set)
    def __eq__(self, other):
        return self.lines == other.lines

    def __hash__(self):
        return hash(str(self.lines))

    def __str__(self):
        return "%s (%s)" % (self.street, ", ".join(self.lines))


