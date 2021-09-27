from qgis.core import *
from PyQt5.QtCore import QVariant

from .pocurrentw import Pocurrentw

class PoQgsCurrentw(Pocurrentw):

    def __init__(self):
        """init class"""
        super(PoQgsCurrentw, self).__init__()
        # or
        # PoStations.__init__(self)

        self.fields = QgsFields()

        self.fnames = ('uuid', 'shortname', 'timestamp', 'value', 'trend', 'stateMnwMhw', 'stateNswHsw')
        self.ftypes = (QVariant.String, QVariant.String, QVariant.DateTime, QVariant.Double, QVariant.Int, QVariant.String, QVariant.String)

        for i in range(len(self.fnames)):
            self.fields.append(QgsField(self.fnames[i], self.ftypes[i]))


    def getFeatures(self):
        """Read Pegelonline Stations as QGIS-Features"""
        data = self.getData()

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
