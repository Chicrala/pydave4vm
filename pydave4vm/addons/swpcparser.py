# !/usr/bin/env python3
#  -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 15:19:08 2018

@author: andrechicrala
"""
import glob
import re
from datetime import datetime, timedelta
from pydave4vm.addons import stdconfig

def find_between(s, first, last):
    '''
    taking a determined string that is inside a long string
    '''
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
def parse_lat_lon(texto):
    '''
    This function will pass the values of
    latitude and longitude from string to
    integers.
    
    They are orientated with north and east
    as being the positive directions.
    '''
    # Getting the numbers.
    latitude = int(texto[1:3])
    longitude = int(texto[4:6])
    
    # Correcting the orientation if needed.
    if texto[0] == 'S':
        latitude = -1*latitude
        
    if texto[3] == 'E':
        longitude = -1*longitude
    
    return(latitude, longitude)

def event_seeker(os_,*args):
    '''
    This function will open an events file and look for each line if the given 
    AR (specified by its NOAA number) is there. If so, this function should 
    grab the entries and return them.
    
    Note: for the sake of simplicity I will leave all the SRS files in the
    same folder.
    '''
    
    # Defaulting path if none is given.
    path = stdconfig.readconfig(os_,'swpc')+'Events/'    
        
    # Listing the items within the directory.
    files = sorted(glob.glob(path+'*events.txt'))
    
    # Creating an empty array to store the data.
    events = {}
    
    # Looping over all the NOAA numbers provided.
    for noaa_number in args[0]:
    
        # Looping over each file.
        for file in files:
            
            # getting the daystamp
            daystamp = find_between(file, 'Events/', 'events.txt')
        
            # opening file
            f = open(file, 'r')
                
            # reading the lines
            text = f.readlines()
            
            # Finding the index of the lines that contain the information we about 
            # the ARs with sunspots.
            for k,j in enumerate(text):
                if '#-----------' in j:
                    # Defining the index of the first line.
                    first_line = k
            
            # Filtering the event numbers, using set will eliminate redundant 
            # entries the minimum line length will help the code to avoid running
            # into empty lines to perform the check which would crash the code.
            event_numbers = list(set([line.split()[0] for line in text[first_line:] \
                                     if len(line) > 20 and str(noaa_number)[1:] in line.split()[-1]\
                                     and ('XRA' or 'FLA' in line)]))
            
            # The counter!
            i = 1
        
            # Taking the XRA for the events
            for number in sorted(event_numbers):
                # Filtering with the event numbers and parsing the information.
                for line in text[first_line:]:
                    if len(line) > 20 and 'XRA' in line and number in line.split()[0]:
                        
                        # checking if the given event is not empty
                        # breaking the line that was given and
                        # storing the linebreak in a dummy variable
                        dummy = [x for x in line.split() if x != '+']
                        
                        # creating the temporal variables
                        event_begin = datetime.strptime(daystamp+dummy[1], '%Y%m%d%H%M')
                        event_begin_int = int(daystamp+dummy[1])
                        
                        # checking for missing data and
                        # testing if the event dates didn't lost meaning for
                        # being in different days. Possible manual error on
                        # making the files.
                        if dummy[2] == '////':
                            event_max = None
                            event_max_int = None
                        
                        else:
                            event_max = datetime.strptime(daystamp+dummy[2], '%Y%m%d%H%M')
                            if event_max < event_begin:
                                try:
                                    event_max += timedelta(days=1)
                            
                                except TypeError:
                                    event_max = None
                                
                                else:
                                    pass
                        
                            # Creating the integer stamp.
                            event_max_int = int(event_max.strftime('%Y%m%d%H%M'))
                        
                        if dummy[3] == '////':
                            event_end = None
                            event_end_int = None
                        
                        else:
                            event_end = datetime.strptime(daystamp+dummy[3], '%Y%m%d%H%M')
                            if event_end < event_begin:
                                event_end += timedelta(days=1)
                                
                            event_end_int = int(event_end.strftime('%Y%m%d%H%M'))
                                
                        
                        # Adding the new event.
                        events.update({str(noaa_number)+'_'+daystamp+'_'+str(i): {'Event': int(number),
                                                                                  'Begin': event_begin,
                                                                                  'Max': event_max,
                                                                                  'End': event_end,
                                                                                  'Beginint': event_begin_int,
                                                                                  'Maxint': event_max_int,
                                                                                  'Endint': event_end_int,
                                                                                  'daystamp_dt': datetime.strptime(daystamp, '%Y%m%d'),
                                                                                  'daystamp_int': int(daystamp),
                                                                                  'Class': re.search(r'[BCMX][0-9].[0-9]',line)[0],
                                                                                  'noaa_number': noaa_number}})
                        # Adding to the counter.
                        i += 1
            
            
    # getting rid of the null entries
    events = {key: value for (key,value) in events.items() if value != {}}
        
    return(events)
    
def morphology_seeker(os_, *args):
    '''
    This function will open an SRS file
    and look for each line if the given AR
    (specified by its NOAA number) is there.
    If so, this function should grab the
    entries and return them.
    
    Note: for the sake of simplicity I 
    will leave all the SRS files in the
    same folder.
    '''
    # assigning
    path = stdconfig.readconfig(os_,'swpc')+'SolarRegionSummary/SRS/'
    print(path)        
    # Listing the items within the directory.
    files = sorted(glob.glob(path+'*.txt'))
    
    # Creating an empty dictionary to store the results.
    morphologies = {}
    
    # Unpacking arguments.
    for noaa_number in args[0]:
        # Looping over each file.
        for file in files:
        
            # Opening file.
            f = open(file, 'r')
            
            daystamp = find_between(file, 'SRS/', 'SRS.txt')
                
            # Reading the lines.
            text = f.readlines()
            
            # Finding the index of the lines that contain the information
            # we about the ARs with sunspots.
            for i,j in enumerate(text):
                if 'I.  Regions with Sunspots.' in j:
                    # Defining the index of the first line.
                    first_line=i
                    
                if 'IA. H-alpha Plages without Spots.' in j:
                    # Defining the index of the last line.
                    last_line=i
            
            # Looping over each line in the text.
            for line in text[first_line+1:last_line]:
                # Checking if the noaa number is mentioned in the given line.
                if str(noaa_number)[1:] in line.split()[0]:
                    # Splitting the line based on the spaces.
                    data = line.split()
                    
                    # Checking if the region went down to plage which would 
                    # present a null entry on the last column.
                    if len(data) < 8:
                        print(f'ALAAAAARM {daystamp}')
                        continue
                    
                    else:
                        # Separating latitude and longitude.
                        latitude, longitude = parse_lat_lon(data[1])
                        # Updating the dictionary.
                        morphologies.update({str(noaa_number)+'_'+daystamp: {'daystamp_int': int(daystamp),
                                                                             'daystamp_dt': datetime.strptime(daystamp, '%Y%m%d'),
                                                                             'Lo': int(data[2]),
                                                                             'area': int(data[3]),
                                                                             'mcintosh': data[4],
                                                                             'LL': int(data[5]),
                                                                             'NN': int(data[6]),
                                                                             'hale': data[7],
                                                                             'latitude': latitude,
                                                                             'longitude': longitude,
                                                                             'noaa_number':noaa_number
                                                                             }})
     
    return(morphologies)

if __name__ == "__main__":
    '''
    The classic testing zone
    '''
    
    morphologies = morphology_seeker(None,[12443,12445])
