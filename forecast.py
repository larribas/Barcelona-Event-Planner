# !/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import urllib2
import time

class ForecastUnavailable(Exception):
    pass


class Forecaster(object):
    """
    Retrieves and processes information about the weather forecast in Barcelona for the next 1-2 days
    """

    FORECAST_URL = 'http://static-m.meteo.cat/content/opendata/ctermini_comarcal.xml'
    BARCELONA_ID = '13'
    LOW_RAIN_PROBABILITY = '1'

    def __init__(self):
        self.forecast_xml = ET.fromstring(urllib2.urlopen(self.FORECAST_URL).read()).find("prediccio[@idcomarca='%s']" % self.BARCELONA_ID)
        self.rain_probabilities = {day.get('data'): self.LOW_RAIN_PROBABILITY not in [day.get(p) for p in ['probcalamati', 'probcalatarda']] for day in self.forecast_xml.findall("variable")}

    def will_it_rain(self, date):
        date = time.strftime("%d-%m-%y", date)

        try:
            return self.rain_probabilities[date]
        except KeyError as ke:
            raise ForecastUnavailable("There is no forecast for the event's date, %s" % date)



