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

def createconfig():
    '''
    This function creates a config file.
    The format for tstart and tend is:
        '2014-01-01T00:00:00'
        or
        '2016.05.18_00:00:00'
    '''
    
    # Defining the configuration file name.
    configfile_name = 'paths.ini'
    
    # Checking if the file exists.
    if not os.path.isfile(configfile_name):
        
        # create the config file if it does not exist yet.
        configfile = open(configfile_name, 'w')
        
        # creating a configparser instance.
        Config = configparser.ConfigParser()
        
        # Adding content to the file. Adding a section.
        Config.add_section('Paths_linux')
        
        # Adding an item. Note that it only accept strings.
        Config.set('Paths_linux', 'data', '/media/w17016451/usb1/data/')
        Config.set('Paths_linux', 'maindb', '/media/w17016451/usb1/databases/main.db')
        Config.set('Paths_linux', 'arsdb', '/media/w17016451/usb1/databases/ARsdb.db')
        Config.set('Paths_linux', 'configs', '/media/w17016451/usb1/configs/')
        Config.set('Paths_linux', 'swpc', '/media/w17016451/usb1/SWPC/')
        
        # Adding a new section.
        Config.add_section('Paths_mac')
        
        # Adding an item. Note that it only accept strings.
        Config.set('Paths_mac', 'data', '/Volumes/Chicrala/data/')
        Config.set('Paths_mac', 'maindb', '/Volumes/Chicrala/databases/main.db')
        Config.set('Paths_mac', 'arsdb', '/Volumes/Chicrala/databases/ARsdb.db')
        Config.set('Paths_mac', 'configs', '/Volumes/Chicrala/databases/configs/')
        Config.set('Paths_mac', 'swpc', '/Volumes/Chicrala/databases/SWPC/')
        
        # Writting the configurations.
        Config.write(configfile)
        
        # Closing file.
        configfile.close()
        
    return


def readconfig(os,option):
    '''
    This function will read the config file and return its parameters.
    '''
    # Creating a configparser instance.
    config = configparser.ConfigParser()
    
    # Reading the configuration file.
    config.read('paths.ini')
    
    options = {'linux':{'data':config['Paths_linux']['data'],
                        'maindb':config['Paths_linux']['maindb'],
                        'arsdb':config['Paths_linux']['arsdb'],
                        'configs':config['Paths_linux']['configs']},
               'mac':{'data':config['Paths_linux']['data'],
                        'maindb':config['Paths_linux']['maindb'],
                        'arsdb':config['Paths_linux']['arsdb'],
                        'configs':config['Paths_linux']['configs']}}
    
    # Checking the option
    
    # Making a try/except statement.
    try: 
        # Getting the parameters.
        path = options[os][option]
        
    except:
        # Printing an error message.
        print('The parameters could not have been read.')
    
    return(path)

if __name__ == '__main__':
    '''
    Test zone.
    '''
    #creating the configfile
    createconfig()
    
    #a = readconfig('mac','data')
    print('a')
    #reading
    #a, b, c, d, e = readconfig('/Users/andrechicrala/Downloads/configs/666config.ini', display = True)

