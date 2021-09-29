# modul poqgsstations
from qgis.core import *
from PyQt5.QtCore import QVariant

from .postations import PoStations

class PoQgsStations(PoStations):

    def __init__(self):
        """init class"""
        super(PoQgsStations, self).__init__()

        self.fields = QgsFields()

        self.fnames = ('uuid', 'number', 'shortname', 'longname', 'km', 'agency', 'water')
        self.ftypes = (QVariant.String, QVariant.Int, QVariant.String, QVariant.String, QVariant.Double, QVariant.String, QVariant.String)


    def getFeatures(self):
        """Read Pegelonline Stations as QGIS-Features"""
        data = self.getData()

        for i in range(len(self.fnames)):
            self.fields.append(QgsField(self.fnames[i], self.ftypes[i]))

        # Processing
        features = []
        for d in data:
            f = QgsFeature(self.fields)

            geom = QgsGeometry.fromPointXY( QgsPointXY(d['geometry'][0], d['geometry'][1]) )

            attributes = d['attributes']

            f.setAttributes(attributes)
            f.setGeometry(geom)

            features.append(f)

        return features