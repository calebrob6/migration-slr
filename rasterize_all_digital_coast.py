#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# pylint: skip-file
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''Code for processing raw digital coast shapefiles.
'''
import sys, os, time, math, csv
import itertools
import collections

import numpy as np

import fiona
from fiona.transform import transform_geom

from shapely.geometry import mapping, shape
from shapely.ops import transform

from rtree import index

import rasterio
import rasterio.mask

def get_slr_layers(fn, slr_amount):
    layers = fiona.listlayers(fn)
    for layer in layers:
        if "_slr_%dft" % (slr_amount) in layer:
            yield layer


def main():

    if len(sys.argv) < 2:
        print("Usage ./rasterize_all_digital_coast.py directory/to/data/")
        return

    BASE_DIR = sys.argv[1]

    for slr_amount in range(7):
        
        output_base = "data/intermediate/digital_coast/slr_%dft/" % (slr_amount)
        if not os.path.exists(output_base):
            os.makedirs(output_base)
        
        for fn in os.listdir(BASE_DIR):

            if fn.endswith(".gdb"):
                fn = os.path.join(BASE_DIR, fn)
                print("\t", fn)
                
                for layer in get_slr_layers(fn, slr_amount):
                    output_fn = "%s%s.tif" % (output_base, layer)

                    if not os.path.exists(output_fn):
                        print("\t\t", layer)
                        
                        # Load layer
                        tic = float(time.time())
                        layer_geoms = []
                        f = fiona.open(fn, layer=layer, mode="r")
                        source_schema = f.schema.copy()
                        src_crs = f.crs["init"]
                        is_correct_projection = src_crs == "epsg:4269"
                        print("\t\tNeed to perform CRS transformation")
                        for s in f:
                            geom = s['geometry']
                            if not is_correct_projection:
                                geom = transform_geom(src_crs, "epsg:4269", geom)
                            s['geometry'] = geom
                            layer_geoms.append(s)
                        f.close()
                        
                        f = fiona.open("tmp.shp", "w", driver="ESRI Shapefile", crs=from_epsg(4269), schema=source_schema)
                        for s in layer_geoms:
                            f.write(s)
                        f.close()    
                        print("\t\tFinished loading layer in %0.4f seconds" % (time.time() - tic))
                        
                        tic = float(time.time())
                        command = [
                            "gdal_rasterize",
                            "-a", "Shape_Area",
                            "-ot", "Float32",
                            "-of", "GTiff",
                            "-a_nodata", "-1",
                            "-tr", "0.001", "0.001",
                            "-co", "COMPRESS=DEFLATE",
                            "-co", "PREDICTOR=1",
                            "-co", "ZLEVEL=6",
                            "-co", "TILED=NO",
                            "-co", "BIGTIFF=YES",
                            "-co", "NUM_THREADS=ALL_CPUS",
                            #"-l", layer,
                            "tmp.shp",
                            output_fn 
                        ]
                        
                        print(" ".join(command))
                        subprocess.call(command)            
                        print("\t\tFinished rasterizing layer in %0.4f seconds" % (time.time() - tic))

                        os.remove("tmp.shp")
                    else:
                        print("%s already exists, skipping" % (output_fn))

if __name__ == "__main__":
    main()