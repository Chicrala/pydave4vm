#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This algorithm should prepare the datacubes to be used on the calling for
dave4vm. It will be necessary to adapt the path where the fits are located.

I guess that this code can actually be used for general pourposes to create 
datacubes with SDO files.

v2:
There is a minor difference in the number of results that will be returned.
Since only one meta data is needed, only one will be returned. Also,
this version receives only the main path and work out the others

V3:
This version is a little more optmized to do only pairs of fits per time.
The counter from the for loop is imported to keep track of the changes


@author: andrechicrala
"""
# Importing packages.
from datetime import datetime

import astropy.units as u

from sunpy.physics.differential_rotation import diff_rot

import sqlalchemy as sql

# Importing the SWPC database packages.
from and_db.ARsdb import Morfologia, Eventos
from and_db.swpcminer import minersession

def parse_prefix(line, fmt):
    '''
    SO/questions/5045210/
    Cheers:
    @Adam Rosenfield.
    '''
    try:
        t = datetime.strptime(line, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            line = line[:-(len(v.args[0]) - 26)]
            t = datetime.strptime(line, fmt)
        else:
            raise
    return t
    
def find_noaa_number(meta_data):
    '''
    This function will use the latitute and longitude of a SHARPs file to
    consult the SWPC Solar Region Summary files, that were parsed to a 
    database, to check what is the NOAA numbers are assigned to the regions
    covered by the SHARP field of view.
    
    The entry for this function is the metadata of the SHARP which NOAA number
    is being search.
    '''
    # Finding the daystamp of this SHARP.
    daystamp = parse_prefix(meta_data['date-obs'], '%Y-%m-%d')
    
    # Finding the timestamp of this SHARP.
    timestamp = datetime.strptime(meta_data['date-obs'], "%Y-%m-%dT%H:%M:%S.%f")
    
    # Calculating the timedelta in seconds and giving the correct unit.
    deltat = (timestamp-daystamp).seconds * u.second
                     
    # Starting the session for the ARs database.
    swpcsession = minersession()
    
    # Making the database selection.
    swpcs = sql.select([Morfologia.longitude,
                        Morfologia.latitude,
                        Morfologia.noaa_number]).where(sql.and_(Morfologia.daystamp_dt == daystamp,
                                                                Morfologia.latitude > meta_data['lat_min'],
                                                                Morfologia.latitude < meta_data['lat_max']))
    
    # Creating an empty list to append the NOAA numbers later on.
    noaa_numbers = []
    
    # Querying the database.
    rp = swpcsession.execute(swpcs)
    
    # Iterating over the results.
    for result in rp:
        # Rotating the Longitude.
        rotated_longitude = result[0]*u.deg + diff_rot(deltat, result[1]*u.deg)
        
        # Checkin if it falls within the box.
        if rotated_longitude > meta_data['lon_min']*u.deg and rotated_longitude < meta_data['lon_max']*u.deg:
            # Fetching the NOAA number
            noaa_numbers.append(result[2])
    
    # Closing the session.
    swpcsession.close()
    
    return(noaa_numbers)
    
def find_morphology(*args):
    '''
    This function will use the noaa number to query the database made from the
    SRS files of SWPC and get the morphology information stored in there.
    '''
    
    # Starting the session for the ARs database.
    swpcsession = minersession()
    
    # Creating an empty dictionary to store the results.
    results = {}
    
    # Looping over each arg.
    for noaa_number in args:
        # Making the database selection.
        swpcs = sql.select([Morfologia]).where(Morfologia.noaa_number==noaa_number)
        
        # Querying the database.
        rp = swpcsession.execute(swpcs)
        
        # Getting the results.
        results[str(noaa_number)] = rp.fetchall()
    
    # Closing the session.
    swpcsession.close()
    
    return(results)
    
def find_events(*args):
    '''
    This function will use the noaa number to query the database made from the
    SRS files of SWPC and get the morphology information stored in there.
    '''
    
    # Starting the session for the ARs database.
    swpcsession = minersession()
    
    # Creating an empty dictionary to store the results.
    results = {}
    
    # Looping over each arg.
    for noaa_number in args:
        # Making the database selection.
        swpcs = sql.select([Eventos]).where(Eventos.noaa_number==noaa_number)
        
        # Querying the database.
        rp = swpcsession.execute(swpcs)
        
        # Getting the results.
        results[str(noaa_number)] = rp.fetchall()
    
    # Closing the session.
    swpcsession.close()
    
    return(results)

if __name__ == '__main__':
    '''
    The classical testing zone
    '''
    results = find_events(12443,12445,12447)