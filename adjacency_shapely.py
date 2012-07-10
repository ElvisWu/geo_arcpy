#!/usr/bin/python
import ogr, gdal, os, sys, MySQLdb
from shapely import *

infile = raw_input("Please enter the path of your geo object: ")

(out_path, file_name) = os.path.split(infile)

driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.Open(infile, 0)
if ds is None:
    print 'Could not open file'
    sys.exit(1)

layer = ds.GetLayer()

feature = layer.GetNextFeature()
while feature:
    
    neighbors = feature.touches(layer)
    gdal.