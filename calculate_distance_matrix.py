#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Script for calculating a pairwise distance matrix from shapefile.

This script takes as input: a shapefile, the name of the column in the shapefile that has the GEOIDs of each shape, and a list of GEOIDs to include in the distance calculation.

This script expects the shapefile to be 2D and in wgs84 format, i.e. having lat/lon coordinates. 

It outputs a pairwise distance matrix between the centroids of the shapes in the shapefile, and a CSV file with the centroids for each GEOID.
This distance matrix will be in the same order as the list of GEOIDs to be included, and the distances will be in kilometers.
'''
import sys
import time

import numpy as np
import haversine
import scipy.spatial
import fiona
import shapely.geometry 

def main():

    if len(sys.argv) != 6:
        print("Usage: python calculateDistanceMatrix.py path/to/inputShapefile.shp shapefileGEOIDKey path/to/inputGEOIDList.txt output/distanceMatrix.npy output/centroidList.csv")
        return 
    
    print("Starting")
    startTime = float(time.time())

    shpFn = sys.argv[1]
    geoidKey = sys.argv[2]
    geoidListFn = sys.argv[3]
    outputFn = sys.argv[4]
    outputCentroidFn = sys.argv[5]

    f = open(geoidListFn,"r")
    acceptedGeoids = f.read().strip().split("\n")
    acceptedGeoidSet = set(acceptedGeoids)
    f.close()

    sf = fiona.open(shpFn)
    usedGeoids = set()
    data = []
    for row in sf:
        geoid = row["properties"][geoidKey]
        if geoid in acceptedGeoidSet:
            usedGeoids.add(geoid)
            geom = shapely.geometry.shape(row['geometry'])
            lon,lat = geom.centroid.x, geom.centroid.y
            data.append((geoid, lon, lat))
        else:
            print("GEOID %s not in accepted list" % (geoid))
    sf.close()

    # report whether we matched all geoids in the input list
    missingGeoids = acceptedGeoidSet - usedGeoids
    if len(missingGeoids) == 0:
        print("All GEOIDs from the accepted list were found in the shapefile")
    else:
        print("The following GEOIDs are in the accepted list, however are not in the shapefile:")
        for geoid in missingGeoids:
            print(geoid)


    print("Loaded %d centroid points in %0.4f seconds" % (len(data), time.time()-startTime))
    
    data = sorted(data)

    f = open(outputCentroidFn,"w")
    f.write("geoid,lon,lat\n")
    for fipsCode,lon,lat in data:
        f.write("%s,%f,%f\n" % (fipsCode,lon,lat))
    f.close()
    
    coords = [(coord[2], coord[1]) for coord in data]

    distanceMatrix = scipy.spatial.distance.cdist(coords,coords,haversine.haversine)

    np.save(outputFn,distanceMatrix)
    
    print("Finished in %0.4f seconds" % (time.time()-startTime))

if __name__ == "__main__":
    main()