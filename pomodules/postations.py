from . import poBaseURL
from .urlreader import Urlreader

class PoStations:
    def __init__(self):
	    self.url = poBaseURL + 'stations.json'

    def getData(self):
        ur = Urlreader(self.url)
        json_data = ur.getJsonResponse()

        # process all stations
        stations = []

        for d in json_data:
            try:
                station = {
                    'geometry': (d['longitude'], d['latitude']),
                    'attributes': [ d['uuid'],
    					d['number'],
    					d['shortname'],
    					d['longname'],
    					d['km'],
    					d['agency'],
    					d['water']['longname']
    				  ]
                }
                stations.append(station)
            except KeyError as e:
                print("WARNING: Station dict %s can't be created. KeyError:%s"%(d,e))

        return stations

