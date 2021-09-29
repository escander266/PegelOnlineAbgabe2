from qgis.core import *
# from pomodules.postations import PoStations
from pomodules.poqgsstations import PoQgsStations


postats = PoQgsStations()
result = postats.getFeatures()

crs = QgsCoordinateReferenceSystem(4326)
writer = QgsVectorFileWriter(r"c:\tmp\postations.shp", "UTF-8", postats.fields, QgsWkbTypes.Point, crs, "ESRI Shapefile")
for f in result:
    writer.addFeature(f)
del writer