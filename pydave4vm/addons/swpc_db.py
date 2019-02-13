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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from pydave4vm.addons import stdconfig

# Importing the SWPC database packages.
from and_db.ARsdb import Base, ARs, Morfologia, Eventos

def minersession(dbaddress = None):
    '''
    This function will create the connection to
    support other functions that will interact
    with the database.
    '''
    # Testing if dbaddress existis defaulting if not.
    while dbaddress is None:
        # Possible location for my db.
        locations = ['/Users/andrechicrala/Downloads/SWPC/ARsdb.db',
                     stdconfig.readconfig('linux','arsdb'),
                     stdconfig.readconfig('mac','arsdb'),
                     ]
        
        # Checking all the possible locations.
        for item in locations:
            # Check if the item exist.
            if os.path.isfile(item) is True:
                # Assign the value if it does.
                dbaddress=item
        
        # Checking if the database is still not there.
        if dbaddress is None:
            # Feedback.
            print('The database could not be located in the usual paths:\n',
                  locations[0],'\n', locations[1], '\n',
                  'Please, check if the database is connected.')
            
            # Checking if it should retry.
            _=input('Retry? (y/n): ')
            if _=='n':
                # Killing the loop.
                break
    
    # Completing the address to the sqlite server.
    dbaddress = 'sqlite:///'+dbaddress
    
    # Creating the engine.
    engine = create_engine(dbaddress)
    
    # Declaratives can be accessed through a DBSession instance.
    Base.metadata.bind = engine
    
    # Binding the engine.
    DBSession = sessionmaker(bind = engine)
    
    # Binding the object methods.
    session = DBSession()
    
    return(session)

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
    
    # Iterating over the results.
    for result in swpcsession.execute(swpcs):
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
    for noaa_number in args[0]:
        # Making the database selection.
        swpcs = sql.select([Morfologia]).where(Morfologia.noaa_number == noaa_number)
        
        # Getting the results.
        results[str(noaa_number)] = [x for x in swpcsession.execute(swpcs)]
    
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
        swpcs = sql.select([Eventos]).where(Eventos.noaa_number == noaa_number)
        
        # Getting the results.
        results[str(noaa_number)] = [x for x in swpcsession.execute(swpcs)]
    
    # Closing the session.
    swpcsession.close()
    
    return(results)
    
def find_max_hale_class(*args):
    '''
    This function will use the noaa number to query the database made from the
    SRS files of SWPC and get the morphology information stored in there.
    '''
    
    # Starting the session for the ARs database.
    swpcsession = minersession()
    
    # Creating an empty dictionary to store the results.
    results = []
    
    # Looping over each arg.
    for noaa_number in args[0]:
        # Making the database selection.
        swpcs = sql.select([ARs.maxhaleclass]).where(ARs.noaa_number == noaa_number)
        
        # Making the result proxy.
        rp = swpcsession.execute(swpcs)
        # Getting the results.
        results.append(rp.fetchone()[0])
    
    # Closing the session.
    swpcsession.close()
    
    return(results)

def test_find_noaa_number(hnum):
    import sunpy.map
    import glob
    print('Testing getting the noaa numbers.')
    #results = find_events(12443,12445,12447)
    #swpcsession = minersession()
    noaa_numbers = []
    paths = glob.glob(f'/media/w17016451/usb1/data2/{hnum}/*Bp.fits')
    for path in paths:
        meta = sunpy.map.Map(path).meta
        noaa_number = find_noaa_number(meta)
        if noaa_number not in noaa_numbers and noaa_number != []:
            print(f'New NOAA number found: {noaa_number}')
            noaa_numbers.append(noaa_number)

    print('NOAA NUMBERS: ', noaa_numbers)
    return(noaa_numbers)
    
if __name__ == '__main__':
    '''
    The classical testing zone
    '''
    '''
    harps = [2587,3686,3688,4448,5011,5026,6223,6555,6558,6620,6846,7256]
    for hnum in harps:
        print(f'Testing {hnum}.')
        noaa_numbers = test_find_noaa_number(hnum)
        print('Testing finding the max hale class.')
        for noaa_number in noaa_numbers:
            print('Getting the morphologies for: ',noaa_number, ' \n ', find_morphology(noaa_number))
            print('The max hale class for this region is: ', find_max_hale_class(noaa_number))
        print('-------------------------------------------------------------------------- \n')
    '''
    #a = find_max_hale_class(12443,12445,None)
    #print(a)
    import sunpy.map
    import glob
    path = '/Volumes/Chicrala/data/3686/*.Bp.fits'
    for file in sorted(glob.glob(path)):
        print(file)
        nn = find_noaa_number(sunpy.map.Map(file).meta)
        print(nn)
