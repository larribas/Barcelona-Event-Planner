Barcelona-Event-Planner
=======================

Python script that outputs information about future events taking place in Barcelona, along with the best transport alternatives to get there.

# Requirements

* A version of Python > 2.6.4 is needed
* This script relies on some cloud services. Should their URLs not be available, the script would fail. These are:
  * [Bicing Stations](http://wservice.viabicing.cat/v1/getstations.php?v=1)
  * [Events in Barcelona](http://w10.bcn.es/APPS/asiasiacache/peticioXmlAsia?id=199)
  * [Weather Forecast for Catalonia](http://static-m.meteo.cat/content/opendata/ctermini_comarcal.xml)
  

# Usage

The script can be invoked via

```
python main.py 'k:v, [k:v, [k:v, [...]]]'
```

Where each ``k:v`` pair corresponds to a query. The event's __k__ should contain the value __v__. For instance,

```
python main.py 'nom:actuacio, nom:ratonera'
```

Would look for all the events whose name contains both _actuacio_ and _ratonera_.

Allowed query attributes are:
* nom (name)
* lloc (place)
* barri (neighborhood)


# Results

After running the script, the obtained results should be under the folder ``Output/``, named by the datetime at which the script was invoked

_N.B. The command ``make clean`` cleans the compiled python files, alongside the generated outputs_

# Motivation
_This project was developed as an assignment for [FIB/GRAU-LP]_
