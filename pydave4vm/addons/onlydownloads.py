#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code will download the data based on the config files within a directory.
@author: andrechicrala
"""

# Importing packages to perform operations in the code.
from datetime import datetime
import logging
import fnmatch
from pydave4vm.addons import myconfig, stdconfig, downloaddata, check_fits

# Importing system related packages.
import glob
import os

def makedownloads(config_path, os_):
    '''
    This is the a code that will
        
    '''
    
    # Creating a timestamp for the analysis start.
    analysis_start = datetime.now()
    
    # Reading the config file.
    harpnum, tstart, extent, cadence, dbaddress,\
    window_size, = myconfig.readconfig(config_path)
    
    # Starting the log file.
    logging.basicConfig(filename = str(harpnum)+'download.log',
                        level=logging.DEBUG)
    
    # Logging when the analysis started.
    logging.info('Downloads started at: ' + str(analysis_start))
    
    #######################################################################
    # Downloading the data.
    #######################    
    # Check in the standard path if file exists.
    std_path = stdconfig.readconfig(os_,'data')+ str(harpnum)+'/'
    # If it don't, download it.
    if os.path.exists(std_path) != True:
    
        # Downloading data and returning the path.
        try:
            path, missing_files = downloaddata.downdrms(harpnum=harpnum,
                                                        tstart=tstart,
                                                        extent=extent,
                                                        cadence=cadence)
            
        # Add to the log if try is sucessfull or not.
        except RuntimeError:
            logging.debug('The download was not complete.')
            print('The download was not complete.')
            
        else:
            logging.info('Downloads finished at: ' + str(datetime.now()))
        
        # Reporting missing files.
        if missing_files != []:
            print(f'Missing files: {missing_files}')
            logging.debug(f'Missing files: {missing_files}')
    
        
    # Checking how many files are inside the directory.
    number_of_files = len(fnmatch.filter(os.listdir(path),'*.fits'))
    
    # And taking the results to the log.
    logging.info('There are ' + str(number_of_files) + 
                ' .fits files saved in the disk.')
    print('There are ' + str(number_of_files) + 
                ' .fits files saved in the disk.')
    
    # Deleting variable.
    del number_of_files
                    
    # Checking if there are 3 files for each magnetic field component.
    Br_unique, Bt_unique, Bp_unique = check_fits.check_fits(path)
    
    # Logging any missing files.
    if Br_unique == [] and Bt_unique == [] and Bp_unique == []:
        logging.info('There are no missing files')
        print('There are no missing files.')
        
    else:
        logging.info('Listing the removed elements: ')
        print('Listing the removed elements: ')
        # Looping over each list to tell which elements were missing.
        for item in Br_unique:
            logging.info(f'{item}')
            print(f'{item}')
            
        for item in Bt_unique:
            logging.info(f'{item}')
            print(f'{item}')
            
        for item in Bp_unique:
            logging.info(f'{item}')
            print(f'{item}')
    
    # Deleting those lists.
    del Br_unique, Bt_unique, Bp_unique
            
    # Shutting down the log.
    logging.shutdown()
    
    return
    
def execute_configs(os_='linux',path=None):
    '''
    This code will read multiple config files and execute the 'prepare' 
    routine for each one of those files which will then make the analysis for 
    each region featured on the file.
    '''
    # Checking if path to configs exists.
    if path is None:
        path = stdconfig.readconfig(os_,'configs')
    
    # Searching for the config files paths.
    path = glob.glob(path+'*.ini')
    
    # Iterating for each congif file.
    for config in path:
        print(f'Initiating the downloads for the file located ar: {config}')
        makedownloads(config_path=config, os_=os_)
    
    # Feedback.    
    print('Finished.')
    
    return

if __name__ == '__main__':
    '''
    test zone
    '''
    execute_configs('linux')
