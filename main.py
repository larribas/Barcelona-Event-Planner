# !/usr/bin/env python
# -*- coding: utf-8 -*-

from output import OutputFormatter
from utils import clean_string, convert_or_raw, GeolocatedObject
from ptransport import PublicTransportProcessor, PublicTransportStation
from bicing import BicingProcessor, BicingStation
from events import EventProcessor, Event
from forecast import Forecaster, ForecastUnavailable

from platform import python_version
import sys
import time


# QUERY-RELATED LOGIC
def get_query_params(raw_query):
	query = {}
	for pair in raw_query.split(","):
		key, value = [clean_string(s) for s in pair.split(":")]
		query[key] = query[key] + [value] if key in query else [value]

	return query

# TRANSPORTATION HYDRATION LOGIC
def find_transportation(event):
		event.will_it_rain = forecaster.will_it_rain(event.date)
		if event.will_it_rain:
			event.nearby_stations_with_slots, event.nearby_stations_with_bikes = bicing.get_stations_near(event)
			if not event.nearby_stations_with_slots or not event.nearby_stations_with_bikes:
				event.nearby_public_transportation_stations = public_transport.get_stations_near(event)
		else:
			event.nearby_public_transportation_stations = public_transport.get_stations_near(event)


if python_version() < '2.6.4':
	print 'You need at least version 2.6.4 of python in order to run this code'
	sys.exit(1)

if len(sys.argv) != 2:
	print "Usage: python main.py 'k:v, [k:v, [k:v, [...]]]'"
	sys.exit(2)

# 1) Parse the query
query = get_query_params(sys.argv[1])

# 2) Get all the events complying with such query
events = EventProcessor().get_events(query)
print 'There are', len(events), 'matching events!'

# 3) For each event, find the appropriate transportation information
if events:
	forecaster = Forecaster()
	bicing = BicingProcessor()
	public_transport = PublicTransportProcessor()

	for event in events:
		try:
			find_transportation(event)
		except ForecastUnavailable:
			event.nearby_stations_with_slots, event.nearby_stations_with_bikes = bicing.get_stations_near(event)
			event.nearby_public_transportation_stations = public_transport.get_stations_near(event)
		except Exception as e:
			event.error = str(e)

# 4) Format and store the output so the user can see it
html = OutputFormatter().output_html(query, events)
output_file = open("Output/output_%s.html" % (time.strftime("%d_%m_%Y__%H_%M")), "w")
output_file.write(html.encode("UTF-8"))
output_file.close()




