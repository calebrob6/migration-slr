#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# pylint: skip-file
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''Docstring
'''
import sys
import os
import time
import datetime
import subprocess

def main():
    prog_name = sys.argv[0]
    print("Starting %s at %s" % (prog_name, str(datetime.datetime.now())))
    start_time = float(time.time())

    base_url = https://www2.census.gov/geo/tiger/TIGER2012/BG/

    state_fips_to_name = {}
    state_name_to_fips = {}
    with open("data/state_fips.csv", "r") as f:
        for line in f:
            line = line.strip()
            if line != "":
                parts = line.split(",")
                
                fips_code = "%02d" % (int(parts[2]))
                state_name = parts[0]

                subprocess.call([
                    "wget",
                    "",
                    "",
                    ""
                ])

    print("Finished in %0.4f seconds" % (time.time() - start_time))

if __name__ == "__main__":
    main()