from . import poBaseURL
from .urlreader import Urlreader

class Pocurrentw:
    def __init__(self):
	    self.url = poBaseURL + 'stations.json?timeseries=W&includeTimeseries=true&includeCurrentMeasurement=true'

    def getData(self):
        """download Data from pegelonline"""
        ur = Urlreader(self.url)
        json_data = ur.getJsonResponse()

        # process all stations
        stations = []
        for d in json_data:
            try:
                currentw = { 'geometry': ( d['longitude'], d['latitude']),
                    'attributes': [ d['uuid'],
                        d['shortname'],
                        d['timeseries'][0]['currentMeasurement']['timestamp'],
                        d['timeseries'][0]['currentMeasurement']['value'],
                        d['timeseries'][0]['currentMeasurement']['trend'],
                        d['timeseries'][0]['currentMeasurement']['stateMnwMhw'],
                        d['timeseries'][0]['currentMeasurement']['stateNswHsw'],
                    ]}
                stations.append(currentw)

            except KeyError as e:
                print("WARNING: Station dict %s can't be created. KeyError:%s"%(d,e))

        return stations
