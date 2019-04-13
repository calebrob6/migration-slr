#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
import os
import csv

import numpy as np

def parse_row_04_08(line):
    ''' This method parses rows from the 2004-2008 IRS migration data.
    
    This data is in a fixed width data format where column names are like the following:
    State_Code_Origin, County_Code_Origin, State_Code_Dest, County_Code_Dest, State_Abbrv, County_Name, Return_Num, Exmpt_Num, Aggr_AGI
    '''
    row = dict()

    row['State_Code_Origin'] = line[0:2].strip()
    row['County_Code_Origin'] = line[3:6].strip()
    row['State_Code_Dest'] = line[7:9].strip()
    row['County_Code_Dest'] = line[10:13].strip()
    row['State_Abbrv'] = line[14:16].strip()
    row['County_Name'] = line[17:49].strip()
    row['Return_Num'] = line[50:59].strip()
    row['Exmpt_Num'] = line[60:70].strip()
    row['Aggr_AGI'] = line[71:82].strip()
    
    return row

def load_file_04_08(fn):
    ''' Method to load 2004-2008 IRS migration data from file.
    '''
    origin_set = set()
    destination_set = set()

    records = []

    f = open(fn, 'r', encoding='ISO-8859-1')
    for line in f:
        line = line.strip()
        if line!='':
            row = parse_row_04_08(line)

            val = int(row['Exmpt_Num'])

            origin = '%02d%03d' % (int(row['State_Code_Origin']), int(row['County_Code_Origin']))
            destination = '%02d%03d' % (int(row['State_Code_Dest']), int(row['County_Code_Dest']))

            origin_set.add(origin)
            destination_set.add(destination)
            records.append((origin,destination,val))
    f.close()

    return records

def load_file_08_11(fn):
    ''' Method to load 2008-2011 IRS migration data from file.
    '''
    origin_set = set()
    destination_set = set()

    records = []

    f = open(fn, 'r', encoding='ISO-8859-1')
    reader = csv.DictReader(f)
    for row in reader:
        val = int(row['Exmpt_Num'])

        origin = '%02d%03d' % (int(row['State_Code_Origin']), int(row['County_Code_Origin']))
        destination = '%02d%03d' % (int(row['State_Code_Dest']), int(row['County_Code_Dest']))

        origin_set.add(origin)
        destination_set.add(destination)
        records.append((origin,destination,val))
    f.close()

    return records


def load_file_11_15(fn):
    ''' Method to load 2011-2015 IRS migration data from file.
    '''
    origin_set = set()
    destination_set = set()

    records = []

    f = open(fn, 'r', encoding='ISO-8859-1')
    reader = csv.DictReader(f)
    for row in reader:
        val = int(row['n2'])

        origin = '%02d%03d' % (int(row['y1_statefips']), int(row['y1_countyfips']))
        destination = '%02d%03d' % (int(row['y2_statefips']), int(row['y2_countyfips']))

        origin_set.add(origin)
        destination_set.add(destination)
        records.append((origin,destination,val))
    f.close()

    return records

class IRSMigrationData(object):

    YEAR_FN_MAP = {
        # year : (dirname, infilename, outfilename),
        2004 : ('county0405','countyin0405us1.dat','countyout0405us1.dat'),
        2005 : ('county0506','countyin0506.dat','countyout0506.dat'),
        2006 : ('county0607','countyin0607.dat','countyout0607.dat'),
        2007 : ('county0708','ci0708us.dat','co0708us.dat'),
        2008 : ('county0809','countyinflow0809.csv','countyoutflow0809.csv'),
        2009 : ('county0910','countyinflow0910.csv','countyoutflow0910.csv'),
        2010 : ('county1011','countyinflow1011.csv','countyoutflow1011.csv'),
        2011 : ('county1112','countyinflow1112.csv','countyoutflow1112.csv'),
        2012 : ('county1213','countyinflow1213.csv','countyoutflow1213.csv'),
        2013 : ('county1314','countyinflow1314.csv','countyoutflow1314.csv'),
        2014 : ('county1415','countyinflow1415.csv','countyoutflow1415.csv'),
    }

    def __init__(self, data_dir='data/raw/migration/'):
        self.data_dir = data_dir
    
    def get_fn_from_year(self, year):
        '''Get paths to the IRS data assosciated with some year.

        Input: year - the year of data to get as an int
        Output: incoming_fn, outgoing_fn - absolute paths to the inflow and outflow data files 
        '''
        if year in IRSMigrationData.YEAR_FN_MAP:
            incoming_fn = os.path.join(self.data_dir, IRSMigrationData.YEAR_FN_MAP[year][0], IRSMigrationData.YEAR_FN_MAP[year][1])
            outgoing_fn = os.path.join(self.data_dir, IRSMigrationData.YEAR_FN_MAP[year][0], IRSMigrationData.YEAR_FN_MAP[year][2])

            return incoming_fn, outgoing_fn
        else:
            raise ValueError('Year %d out of range' % (year))

    def get_raw_data(self, year):
        ''' Get rows from raw IRS migration data files.

        Input: year - the year of data to get as an int
        Output: list incoming and outgoing migrant records from that year in the format (origin, destination, number of exemptions)
        '''
        incoming_fn, outgoing_fn = self.get_fn_from_year(year)

        in_records = None
        out_records = None
        if 2004<=year<2008:
            in_records = load_file_04_08(incoming_fn)
            out_records = load_file_04_08(outgoing_fn)
        elif 2008<=year<2011: 
            in_records = load_file_08_11(incoming_fn)
            out_records = load_file_08_11(outgoing_fn)
        elif 2011<=year<2015:
            in_records = load_file_11_15(incoming_fn)
            out_records = load_file_11_15(outgoing_fn)
        else:
            raise ValueError('Year %d out of range' % (year))

        return in_records, out_records

    def get_processed_data(self, year, county_fips, verbose=False):
        ''' Get migration matrix for a given year and set of county FIPS codes.

        Input: year - the year of data to get as an int
        Output: Migration matrix of size (|county_fips| x |county_fips|) where an i,j entry corresponds to the number of migrants leaving county i for county j
        '''
    
        county_set = set(county_fips)
        assert len(county_set) == len(county_fips), 'List of counties should not have duplicates'
        county_fips_to_idx = {fips:i for i, fips in enumerate(county_fips)}
        n = len(county_fips)

        migration_matrix = np.zeros((n,n), dtype=np.int32)
        
        in_records, out_records = self.get_raw_data(year)

        for origin, destination, val in in_records:
            if 2004<=year<2008: # the 2004 - 2008 data has this backwards
                origin, destination = destination, origin
            
            if origin in county_set and destination in county_set:

                origin_idx = county_fips_to_idx[origin] 
                destination_idx = county_fips_to_idx[destination]

                if origin in county_set and destination in county_set:
                    migration_matrix[origin_idx, destination_idx] = val

        repeats = 0
        discrepancies = 0
        for origin, destination, val in out_records:
            if origin in county_set and destination in county_set:
                origin_idx = county_fips_to_idx[origin] 
                destination_idx = county_fips_to_idx[destination]

                if migration_matrix[origin_idx, destination_idx] != 0:
                    if migration_matrix[origin_idx, destination_idx] != val:
                        repeats += 1
                        discrepancies += abs(migration_matrix[origin_idx, destination_idx] - val)

                migration_matrix[origin_idx, destination_idx] = val
        
        # Sanity check, there should not be any u,v in the in_records that contradict with records from out_records
        if verbose:
            print('Found %d repeats' % (repeats))
            print('Error of %d migrants' % (discrepancies))

        return migration_matrix