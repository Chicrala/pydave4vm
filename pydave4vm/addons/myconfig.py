#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code is responsible to produce and read the config files that will store 
the base parameters responsible to run some of my scripts. Those two features
are separated into two different functions.

harp numbers can be consulted here:
http://jsoc.stanford.edu/data/hmi/HARPs_movies/definitive/

@author: andrechicrala
"""
import configparser
import os
import json    
from pydave4vm.addons import stdconfig

def createconfig(harpnum, tstart, extent,
                 window_size = None,
                 path = None,
                 dbaddress = None,
                 cadence = None,
                 loadstd = False,
                 std_path = None):
    '''
    This function creates a config file.
    The format for tstart and tend is:
        '2014-01-01T00:00:00'
        or
        '2016.05.18_00:00:00'
    '''
    # Checkin if it should load the standard file template with the variables
    # values pre defined by the user.
    if loadstd is True:
        standards = json.load(std_path)
        window_size = standards['window_size']
        path = ['path']
        dbaddress = ['dbaddress']
        cadence = ['cadence']
    
    # Defining the configuration file name.
    configfile_name = path + str(harpnum) + 'config.ini'
    
    # Checking if the file exists.
    if not os.path.isfile(configfile_name):
        
        # create the config file if it does not exist yet.
        configfile = open(configfile_name, 'w')
        
        # creating a configparser instance.
        Config = configparser.ConfigParser()
        
        # Adding content to the file. Adding a section.
        Config.add_section('Parameters')
        
        # Adding an item. Note thatit only accept strings.
        Config.set('Parameters', 'harpnum', str(harpnum))
        Config.set('Parameters', 'tstart', tstart)
        Config.set('Parameters', 'extent', extent)
        Config.set('Parameters', 'cadence', cadence)
        Config.set('Parameters', 'dbaddress', dbaddress)
        Config.set('Parameters', 'window_size', str(window_size))
        
        # Writting the configurations.
        Config.write(configfile)
        
        # Closing file.
        configfile.close()
        
    return


def readconfig(path, display = None):
    '''
    This function will read the config file and return its parameters.
    '''
    
    # Creating a configparser instance.
    config = configparser.ConfigParser()
    
    # Reading the configuration file.
    config.read(path)
    
    # Making a try/except statement.
    try: 
        # Getting the parameters.
        harpnum = int(config['Parameters']['harpnum'])
        tstart = config['Parameters']['tstart']
        extent = config['Parameters']['extent']
        cadence = config['Parameters']['cadence']
        dbaddress = config['Parameters']['dbaddress']
        window_size = int(config['Parameters']['window_size'])
        
    except:
        # Printing an error message.
        print('The parameters could not have been read.')
    
    return(harpnum, tstart, extent, cadence, dbaddress, window_size)

if __name__ == '__main__':
    
    #creating the configfile
    createconfig(harpnum = 4448, tstart = '2014.08.16_00:00:00',
                 extent = '1h', window_size = 20, path = stdconfig.readconfig('linux','configs'),
                 dbaddress = 'sqlite:///'+stdconfig.readconfig('linux','maindb'),
                 cadence = '720s',)
    
    #reading
    #a, b, c, d, e = readconfig('/Users/andrechicrala/Downloads/configs/666config.ini', display = True)

