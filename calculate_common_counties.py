#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Usage: python calculateCommonCounties.py

This script calculates which FIPS are shared between all of the years of migration data.

Creates output/largestCountyIntersection_2004_2014.txt which is a numerically sorted list of FIPS codes in the continental USA that are common across all years of data.
'''
from MigrationDataUSA import loadFile

# List of state prefixes for the FIPS codes of the 48 continental US states
CONTINENTAL_STATE_FIPS = ["01","04","05","06","08","09","10","12","13","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44","45","46","47","48","49","50","51","53","54","55","56"]
assert len(CONTINENTAL_STATE_FIPS) == 48

def main():
    years = range(2004, 2015) # years for which we have data

    fipsSets = [] # a set for each year of data containing *all* the FIPS codes from that year
    for i,year in enumerate(years):
        inRecords,outRecords = loadFile(year)

        fipsSet = set()
        for origin,destination,val in inRecords:
            fipsSet.add(origin)
            fipsSet.add(destination)
        for origin,destination,val in outRecords:
            fipsSet.add(origin)
            fipsSet.add(destination)
        fipsSets.append(fipsSet)

    # a set for each year of data containing the FIPS codes in continental states that are not used for special purposes (county FIPS '000' is reserved')
    newFipsSets = []
    for i,year in enumerate(years):
        fipsSet = fipsSets[i]
        newFipsSet = set()
        for fips in fipsSet:
            stateCode = fips[:2]
            countyCode = fips[2:]
            if stateCode in CONTINENTAL_STATE_FIPS and countyCode!="000":
                newFipsSet.add(fips)

        print("%d -- %d counties" % (year, len(newFipsSet))( 
        newFipsSets.append(newFipsSet)

    print("")

    # calculate the intersection of all sets
    joinedSet = set(newFipsSets[0])
    for s in newFipsSets[1:]:
        joinedSet.intersection_update(s)
    print("Total of %d locations in continental states that are common to all years of data." % (len(joinedSet)))

    print("")

    # sort FIPS code in numerical order
    joinedList = {fipsCode:int(fipsCode) for fipsCode in joinedSet}
    sortedJoinedList = sorted(joinedList, key=joinedList.get)

    # write output
    outputFn = "output/largestCountyIntersection_2004_2014.txt"
    print("Saving list of FIPS common to all years of data to %s" % (outputFn))
    f = open(outputFn, "w")
    for fipsCode in sortedJoinedList:
        f.write("%s\n" % (fipsCode))
    f.close()
    
    print("Finished")

if __name__ == '__main__':
    print(__doc__)
    print("")
    main()