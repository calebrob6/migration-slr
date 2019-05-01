#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import pickle
import hashlib
from mpl_toolkits.basemap import Basemap
import time

import numpy as np
import matplotlib

import fiona
import shapely
import shapely.geometry
import shapely.ops

KWARGS_IGNORE = ["cacheDir","verbose"]

DEFAULT_CACHE_LOCATION = os.path.join(os.path.expanduser("~"), ".BasemapUtilsCache/")

def getBounds(fn):
    '''Takes the filename of a shapefile as input, returns the lat/lon bounds in the form:

    (minLatitude,maxLatitude), (minLongitude,maxLongitude)
    '''
    f = fiona.open(fn)
    bounds = f.bounds # In the format (w, s, e, n)
    f.close()

    return (bounds[1],bounds[3]),(bounds[0],bounds[2])

def getShapefileColumnHeaders(fn):
    '''Returns all of the column headers from a given shapefile
    '''
    f = fiona.open(fn)
    headers = f[0]["properties"].keys()
    f.close()

    return headers

def getShapefileColumn(fn, dataHeader, primaryKeyHeader=None):
    '''Takes the filename of a shapefile, the name of the column of data to extract, and optionally the name of the column of data to use as keys.abs

    If primaryKey is None, then this method will return the a list of all the values in the "dataHeader" column.
    If primaryKey is defined, then this method will return a dict where key=>value pairs are primaryKeyValue=>dataValue for each row.
    '''
    f = fiona.open(fn)
    
    # Check to make sure the column headers are in the file
    headers = f[0]["properties"].keys()
    assert dataHeader in headers, "dataHeader %s not in %s" % (dataHeader, headers)
    if primaryKeyHeader is not None:
        assert primaryKeyHeader in headers, "primaryKeyHeader %s not in %s" % (primaryKeyHeader, headers)
    
    if primaryKeyHeader is not None:
        data = {}
        for row in f:
            primaryKey = row["properties"][primaryKeyHeader]
            if primaryKey not in data:
                data[primaryKey] = row["properties"][dataHeader]
            else:
                raise ValueError("Primary key column is not unique (duplicate value found: %r)" % (primaryKey))
    else:
        data = []
        for row in f:
            data.append(row["properties"][dataHeader])
    
    f.close()

    return data

def getBasemapWrapperHash(*args, **kwargs):
    newKwargs = {}
    for k,v in kwargs.items():
        if k not in KWARGS_IGNORE:
            newKwargs[k] = v

    uniqueRepr = str(set(tuple(newKwargs.items()))).encode('utf-8')
    hashed = str(hashlib.sha224(uniqueRepr).hexdigest())
    return hashed

def getCacheDir(cacheDir,verbose=False):
    if cacheDir is None:
        cacheDir = DEFAULT_CACHE_LOCATION
        if verbose:
            print("cacheDir was not set, using the default location: %s" % (cacheDir))

    outputBase = os.path.dirname(cacheDir)
    if outputBase!='' and not os.path.exists(outputBase):
        if verbose:
            print("Output directory does not exist, making output dirs: %s" % (outputBase))
        os.makedirs(outputBase)

    return outputBase

def shapelyTransformIdentityFunction(x, y, z=None):
    return tuple(filter(None, [x, y, z]))

def getPolygonPatches(transformer, shapefileFn, shapefileKey, filterList=None):

    if transformer is None:
        transformer = shapelyTransformIdentityFunction

    sf = fiona.open(shapefileFn)
    rows = []
    for row in sf:
        rows.append(row)
    sf.close()

    shapes = []
    keys = []

    for i,entry in enumerate(rows):
        geo = entry["geometry"]
        primaryKey = entry["properties"][shapefileKey]

        if filterList is not None:
            if primaryKey not in filterList:
                continue

        if geo["type"]=="MultiPolygon":
            #we need to split each MultiPolygon up into individual ones
            for coordList in entry["geometry"]["coordinates"]:
                newGeo = {
                    "type" : "Polygon",
                    "coordinates" : coordList
                }
                shape = shapely.geometry.shape(newGeo)
                shapes.append(shape)
                keys.append(primaryKey)

        elif geo["type"]=="Polygon": 
            shape = shapely.geometry.shape(geo)
            shapes.append(shape)
            keys.append(primaryKey)
        else:
            raise ValueError("There is some kind of weird shape in shapefile?")

    patches = []
    xMax, xMin = float('-inf'), float('inf')
    yMax, yMin = float('-inf'), float('inf')
    
    for i in range(len(keys)):
        shape = shapes[i]

        newShape = shapely.ops.transform(transformer, shape)

        x,y = newShape.exterior.xy
        tXmin, tXmax = min(x),max(x)
        tYmin, tYmax = min(y),max(y)

        xMax = max(xMax, tXmax)
        xMin = min(xMin, tXmin)
        yMax = max(yMax, tYmax)
        yMin = min(yMin, tYmin)

        polygon = matplotlib.patches.Polygon(np.array([x,y]).T, closed=True, facecolor='grey', zorder=0, alpha=1, linewidth=1)
        
        patches.append(polygon)

    return patches, keys, [(xMin,xMax), (yMin, yMax)]

def PolygonPatchesWrapper(transformer, shapefileFn, shapefileKey, filterList=None, cacheDir=None, basemapArgs=None, verbose=False):
    '''Wrapper around the getPolygonPatches method that will cache the results as a pickled file to reduce long loading times.

    As there isn't a good way to get a general hash of the transformer function, you need to pass the basemapArgs dict to this function
    so it can differentiate between shapefiles loaded with different transformers.
    '''
    outputBase = getCacheDir(cacheDir,verbose=verbose)

    basemapHash = getBasemapWrapperHash(**basemapArgs)

    hashedRepresentation = {
        "basemapHash" : basemapHash,
        "shapefileFn" : shapefileFn,
        "shapefileKey" : shapefileKey,
        "filterList" : ','.join(map(str,filterList)) if filterList is not None else "None"
    }

    uniqueRepr = str(set(tuple(hashedRepresentation.items()))).encode('utf-8')
    hashedFn = str(hashlib.sha224(uniqueRepr).hexdigest()) + ".p"
    newFn = os.path.join(outputBase,hashedFn)

    if os.path.isfile(newFn):
        startTime = float(time.time())
        if verbose:
            print("Loading from file: %s" % (newFn))
        patches, keys, bounds = pickle.load(open(newFn,'rb'))
        if verbose:
            print("Finished loading from file in %0.4f seconds" % (time.time()-startTime))
    else:
        startTime = float(time.time())
        if verbose:
            print("Creating object and saving to file: %s" % (newFn))

        patches, keys, bounds = getPolygonPatches(transformer, shapefileFn, shapefileKey, filterList=filterList)
        pickle.dump([patches, keys, bounds],open(newFn,'wb'),-1)
        if verbose:
            print("Finished creating object and saving to file in %0.4f seconds" % (time.time()-startTime))

    return patches, keys, bounds

def BasemapWrapper(*args, **kwargs):
    '''Wrapper around Matplotlib's Basemap class that caches instantiated Basemap objects with pickle to avoid the longer waittimes
    from creating an object with any of the higher resolution settings (resolution="f" can take minutes to load).

    You should be able to call this method in the same way as a normal Basemap object. For example:

    basemapArgs = {
        "projection":'merc',
        "llcrnrlat":lats[0],
        "urcrnrlat":lats[1],
        "llcrnrlon":lons[0],
        "urcrnrlon":lons[1],
        "resolution":None,
        "fix_aspect":True,
        "suppress_ticks":True,
        # Extra arguments -----------------------------
        "cahceDir="/home/user/.BasemapUtilCache/",
        "verbose":verbose
    }
    m = BasemapWrapper(**basemapArgs)

    Set cacheDir="/absolute/path/to/cache/" as a keyword argument to specify where the pickled objects will be saved.
    Set verbose=True to see what is going on
    '''
    assert len(args)==0, "Shouldn't be calling Basemap with any positional arguments..."

    verbose = False
    if "verbose" not in kwargs:
        verbose = False
    else:
        verbose = kwargs["verbose"]
        assert type(verbose) == bool

    if verbose:
        print("Starting BasemapWrapper")


    cacheDir = kwargs["cacheDir"] if "cacheDir" in kwargs else None
    outputBase = getCacheDir(cacheDir,verbose=verbose)

    newKwargs = {}
    for k,v in kwargs.items():
        if k not in KWARGS_IGNORE:
            newKwargs[k] = v


    hashedFn = getBasemapWrapperHash(**kwargs)
    newFn = os.path.join(outputBase,hashedFn)

    if os.path.isfile(newFn):
        startTime = float(time.time())
        if verbose:
            print("Loading from file: %s" % (newFn))
        m = pickle.load(open(newFn,'rb'))
        if verbose:
            print("Finished loading from file in %0.4f seconds" % (time.time()-startTime))
    else:
        startTime = float(time.time())
        if verbose:
            print("Creating object and saving to file: %s" % (newFn))
        m = Basemap(*args, **newKwargs)
        pickle.dump(m,open(newFn,'wb'),-1)
        if verbose:
            print("Finished creating object and saving to file in %0.4f seconds" % (time.time()-startTime))

    return m


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    getShapefileColumn("examples/cb_2015_us_county_500k/cb_2015_us_county_500k.shp","GEOID")