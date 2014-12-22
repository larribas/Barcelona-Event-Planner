# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class OutputFormatter(object):
    """
    Formats the output of a list of events (potentially it handles many formats) 
    """

    def output_html(self, query, events):

        # Table of contents
        list_of_events = reduce(lambda x,y: x + y, ['<li><a href="#%s">%s</a></li>' % (i, event.name.title()) for i, event in enumerate(events)], '')
        if not list_of_events:
            list_of_events = '<p>There are currently no events matching the specified query</p>'

        table_of_contents = '<div><h2>List of events matching</h2><pre>%s</pre><ul>%s</ul></div>' % (str(query), list_of_events)

        event_info = ''
        for i, event in enumerate(events):
            event_info += '<h2><a id="%s">%s</a></h2>' % (i, event.name.title())
            if hasattr(event, 'error'):
                event_info += '<div class="alert alert-danger" role="alert"><p>An error occured: %s</p></div>' % (event.error)
            event_info += """
                <!-- Event information -->
                <table class="table table-bordered">
                    <thead>
                        <tr><th class="text-center" colspan="2">Event information</th></tr>
                    </thead>
                    <tbody>
                        <tr><th>Name</th><td>%s</td></tr>
                        <tr><th>Place</th><td>%s</td></tr>
                        <tr><th>Address</th><td>%s <a href="http://maps.google.com/maps?z=18&q=%f,%f" target="_blank">(See in Google Maps!)</a></td></tr>
                        <tr><th>Date</th><td>%s</td></tr>
                        <tr><th>Starts at</th><td>%s</td></tr>
                        <tr><th>Ends at</th><td>%s</td></tr>
                    </tbody>
                </table>
                """ % (
                    event.name.title(),
                    event.place,
                    event.address,
                    event.lat if type(event.lat) == float else 0.0,
                    event.lon if type(event.lat) == float else 0.0,
                    time.strftime('%d-%m-%Y', event.date),
                    time.strftime('%H:%M', event.starts_at) if event.starts_at else 'This event has no information about the time it starts at',
                    time.strftime('%H:%M', event.ends_at) if event.ends_at else 'This event has no information about the time it ends at'
                )

            forecast = """
                <!-- Forecast -->
                <table class="table table-bordered">
                    <thead>
                        <tr><th class="text-center">Forecast</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><img class="forecast-icon" src="https://dl.dropboxusercontent.com/u/7089729/%s">%s</td></tr>
                    </tbody>        
                </table>
                """

            if (not hasattr(event, 'will_it_rain')):
                event_info += forecast % ('forecast-error-icon.png', "There is no forecast for the event's date, %s. Therefore, we list all the alternative ways to get there" % time.strftime('%d-%m-%Y', event.date))
            elif (event.will_it_rain):
                event_info += forecast % ('rain-icon.png', 'There is a good chance it will rain on the day of the event, so you will be better off using public transportation.')
            else:
                event_info += forecast % ('partly-cloudy-day-icon.png', "It probably won't rain on the day of the event, so we thought you might enjoy going there by bike.")


            bicing_skeleton = """
                <!-- Bicing Stations -->
                <table class="table table-bordered">
                    <thead>
                        <tr><th colspan="5">
                            <img class="transport-icon" src="https://dl.dropboxusercontent.com/u/7089729/logo-bicing.png">
                            <span class="transport-text">Nearest 5 Bicing stations with {0} available within 500m of the event</span>
                        </th></tr>
                        <tr>
                            <th>#</th>
                            <th>Street</th>
                            <th>Bicing ID</th>
                            <th>{0} available</th>
                            <th>Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        {1}
                    </tbody>
                </table>
                """

            if hasattr(event, 'nearby_stations_with_slots'):
                station_info = ''
                if not event.nearby_stations_with_slots:
                    station_info = '<tr><td colspan="5">At this moment, there are no stations with slots available within 500m of the event. Alternatively, we dislay a list of nearby public transportation stations.</td></tr>'
                else:
                    for i, station in enumerate(event.nearby_stations_with_slots[:5]):
                        station_info += '<tr><td>%d</td><td>%s</td><td>%d</td><td>%d</td><td><a href="http://maps.google.com/maps?z=18&q=%f,%f" target="_blank">See map</a></td></tr>' % (i+1, station.street, station.id, station.slots, station.lat, station.lon)

                event_info += bicing_skeleton.format('slots', station_info)

            if hasattr(event, 'nearby_stations_with_bikes'):
                station_info = ''
                if not event.nearby_stations_with_bikes:
                    station_info = '<tr><td colspan="5">At this moment, there are no stations with bikes available within 500m of the event. Alternatively, we dislay a list of nearby public transportation stations.</td></tr>'
                else:
                    for i, station in enumerate(event.nearby_stations_with_bikes[:5]):
                        station_info += '<tr><td>%d</td><td>%s</td><td>%d</td><td>%d</td><td><a href="http://maps.google.com/maps?z=18&q=%f,%f" target="_blank">See map</a></td></tr>' % (i+1, station.street, station.id, station.bikes, station.lat, station.lon)

                event_info += bicing_skeleton.format('bikes', station_info)


            public_transport_skeleton = u"""
                <!-- Public Transportation Stations -->
                <table class="table table-bordered">
                    <thead>
                        <tr><th colspan="5">
                            <img class="transport-icon" src="https://dl.dropboxusercontent.com/u/7089729/logo-tmb.png">
                            <span class="transport-text">Public transportation stations within 1km of the event</span>
                        </th></tr>
                        <tr>
                            <th>#</th>
                            <th>Kind</th>
                            <th>Lines</th>
                            <th>Street</th>
                            <th>Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        {0}
                    </tbody>
                </table>
                """

            if hasattr(event, 'nearby_public_transportation_stations'):
                station_info = ''
                if not event.nearby_stations_with_slots:
                    station_info = '<tr><td colspan="5">We are sorry. There are no public transportation stations nearby. It looks like you will have to call a <a href="https://www.hailoapp.com/es/">taxi</a></td></tr>'
                else:
                    for i, station in enumerate(event.nearby_public_transportation_stations):
                        station_info += '<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td><a href="http://maps.google.com/maps?z=18&q=%f,%f" target="_blank">See map</a></td></tr>' % (i+1, station.kind, ", ".join(station.lines), station.street if station.street else '-', station.lat, station.lon)

                event_info += public_transport_skeleton.format(station_info)


        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Barcelona Event Planner</title>

                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">

                <style type="text/css">
                    h2 {
                        margin-top: 100px;
                    }

                    h2 a, h2 a:hover {
                        text-decoration: none;
                        color: black;
                    }

                    table.event tbody tr th {
                        width: 10%%;
                    }

                    .forecast-icon {
                        width: 90px;
                        height: 90px;
                        margin-right: 25px;
                    }

                    .transport-icon {
                        float: left;
                        width: 120px;
                        margin-right: 30px;
                    }

                    .transport-text {
                        vertical-align: middle;
                    }

                    footer {
                        margin-top: 200px;
                        margin-bottom: 30px;
                        font-style: italic;
                        float: right;
                    }
                </style>

            </head>
            <body>
                <div class="row">
                    <div class="col-md-offset-2 col-md-8">

                    <h1 class="text-center">Barcelona Event Planner</h1>
                    <p class="text-center">Information about the future events taking place in Barcelona, along with the best alternatives to get there.</p>

                    %s

                    %s

                    <footer>Barcelona Event Planner. Lorenzo Arribas, 2014</footer>

                    </div>
                </div>
            </body>
            </html>
            """ % (table_of_contents, event_info)





