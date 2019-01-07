#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code represents my pre-call for dave4vm algorithm.
Here data is setup to serve as an entry to the actual code that will call dave4vm
which is do_dave4vm_and.py

Here is where one would want to decide what values of the magnetic field should 
be taken into the variables.

v2:
This version is used to run over multiple fits files and export the results.
Also, the time interval between two images is calculated based on the header.

v3:
This version also runs over multiple files but takes the results into the 
database

V4:
This version also has the automation of the downloads, get the
basic parameters to do so from an external file and produces a log.

V4-1:
This version brings some changes on how the results are inserted into
the database. The observations and Dave4vm columns were merged and, thus,
the results are inserted all at once. An option was added to skip the
download phase if data is already in the disk.

V5:
This version will automate the script to interact over multiple config files.
the name "call" was deprecated in favour of "prepare". Varibles references 
for path and downloaded were also improved.

V5-1:
In this version the datacubes are made for each interaction. The full data 
cube processing at once was causing the memory to overload itself.
Also a new module was added to prevent problems related to missing files
during the download. The check_fits module will delete any files that do 
not exist in all the three components.

execute:
Essentially version 5.1. The name has been changed since this will be the 
final version which I intend to exert control over.


use con and get like here:
    https://gist.github.com/maedoc/b5b3cd91aaa59ec573f9
    
    

@author: andrechicrala
"""

#importing basic packages
import numpy as np
from datetime import datetime
#calling my set of packages
from pydave4vm import cubitos3, check_fits, do_dave4vm_and
from and_mods.poyntingflux import poyntingflux
from pydave4vm import downloaddata
from and_mods import myconfig
#importing the packages to create the session
import sqlalchemy as sql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#importing system related packages
import glob
import shutil
import logging
import os
import fnmatch
#importing the classes
from and_db.dbtest import Base, ActiveRegion, Observations
import sys
import sunpy
import sunpy.map

def ajuste(data):
    '''
    Quick function to pass data in a numpy array 
    to string format. Somehow it wasn't working
    inside the main code.
    '''
    
    return(data.tostring())


def prepare(config_path, downloaded = None, delete_files = None):
    '''
    This is the pre-routine to execute pydave4vm.
    Here the following steps are taken:
        
        - The parameters are fetch from an external file;
        - Data is downloaded using drms to query JSOC;
        - The fits are organized into datacubes;
        - Data is inserted into the do_dave4vm_and module;
        - Updates on the database;
        - Log production.
        
    '''
    
    # Creating a timestamp for the analysis start.
    analysis_start = datetime.now()
    
    # Reading the config file.
    harpnum, tstart, extent, cadence, dbaddress,\
    window_size, = myconfig.readconfig(config_path)
    
    # Starting the log file.
    logging.basicConfig(filename = str(harpnum)+'.log',
                        level=logging.DEBUG)
    
    # Logging when the analysis started.
    logging.info('Analysis started at: ' + str(analysis_start))
    
    # Checking if data is already in the disk.
    if downloaded == None:
        
        # Check in the standard path if file exists.
        std_path = '/Users/andrechicrala/Downloads/'+ str(harpnum)+'/'
        # If it don't, download it.
        if os.path.exists(std_path) != True:
        
            # Downloading data and returning the path.
            try:
                path = downloaddata.downdrms(harpnum = harpnum,
                                             tstart = tstart,
                                             extent = extent,
                                             cadence = cadence)
                
            # Add to the log if try is sucessfull or not.
            except RuntimeError:
                logging.debug('The download was not complete.')
                print('The download was not complete.')
                
            
            else:
                logging.info('Downloads finished at: ' + str(datetime.now()))
                
        # If it does use the files there.
        else:
            path = std_path
    
    # Assigning the path to the files.       
    else:
        
        # Checking if the path exists.
        while os.path.exists(downloaded) != True:
            # Inputing the path.
            downloaded = str(input('Inform the path to the downloaded files enclosing folder: '))
        
        # Logging the output.
        logging.info('The files were already saved in the disk.')
        print('The files were already saved in the disk.')
        
        # Assigning the path.
        path = downloaded
        
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
    
    # Checking the number of observations.
    number_of_obs = int(len(fnmatch.filter(os.listdir(path),'*.fits'))/3)
    
    # Taking the information from one of the files.
    meta = sunpy.map.Map(path + os.listdir(path)[0]).meta
    
    # Defining a dx and dy in km based on HMI resolution.
    dx = (2*np.pi*6.955e8*meta['CDELT2']/360)/1000
    dy = dx
    
    ###########################################################################
    # Creating the sql engine:
    engine = create_engine(dbaddress, pool_pre_ping=True)
    
    # Binding the engine to the create the engine later
    #Base.metadata.bind = engine
    
    # Binding the engine
    DBSession = sessionmaker(bind = engine)
    # Creating the session
    session = DBSession()
    
    ###########################################################################
    
    # Check if stamp exist to keep completing it.
    s = sql.select([ActiveRegion]).where(
                ActiveRegion.harp_number == meta['harpnum'])
    
    # Using the result proxy to query the results.
    rp = session.execute(s)
    
    # Fetching all the results.
    AR = rp.fetchall()
    
    #If the AR isn't there yet, insert it into the database.
    if AR == []:
        #the first session should create an item for the active region
        #using its noaa and harp numbers
        #starting session
        try:
            new_ar = ActiveRegion(noaa_number = meta['noaa_ar'],
                                  harp_number = meta['harpnum'])
            session.add(new_ar)
            session.commit()
            
        #adding the atribute exception    
        except AttributeError:
            session.rollback()
            logging.debug('AR not inserted into the database.')
            print('AR not inserted into the database.')
            
        else:
            '''
            Aqui eu posso inserir uma key pra região pra perguntar se ela é
            continuação ou não
            continue True or false
            '''
            # Checking on the ar_id if stamp exist to keep completing it.
            s = sql.select([ActiveRegion]).where(
                        ActiveRegion.harp_number == meta['harpnum'])
            
            # Quqerying and fetching the results
            rp = session.execute(s)
            AR = rp.fetchall()
            
            # Assigning the ar number to a variable.
            ar_id = AR[0][0]
            
            # Checking if the result is an int.
            if type(ar_id) != int:
                #logging
                logging.debug('Inconsistent type for AR id.')
                print('Inconsistent type for AR id.')
                print('Abort Mission!')
                sys.exit('Exiting')
            
            
            logging.info('AR ' + str(meta['harpnum']) + \
                         ' commited into the database. New AR id: ' + \
                         str(ar_id))
            
            # Prints to state progress.
            print('AR ' + str(meta['harpnum']) + \
                         ' commited into the database. New AR id: ' + \
                         str(ar_id))
            
        
    else:
        # Printing which is the table positioning.
        logging.info(f'The Active Region {AR[0][1],AR[0][2]} is already in the '
              f'database with the id: {AR[0][0]}')
        
        print(f'The Active Region {AR[0][1],AR[0][2]} is already in the '
              f'database with the id: {AR[0][0]}')
        
        # Assigning the ar number. Redundant? Check!!!
        ar_id = AR[0][0]
        
        # Checking if the result is an int.
        if type(ar_id) != int:
            #logging
            logging.debug('Inconsistent type for AR id.')
            print('Inconsistent type for AR id.')
            print('Abort Mission!')
            sys.exit('Exiting')
    
    # Looping over all the datacubes. Note that all of them should have the 
    # same dimensions which is already standard for the cea data
    for i in range(len(glob.glob(path+'*.Bp.fits'))-1):
        
        #Calling the cubitos2.py function to make the datacubes.
        data_cube_Br, data_cube_Bp, data_cube_Bt,\
        meta_cube_Bp = cubitos3.create_cube(path, i)
    
        # Defining the start and end points based on the datacubes.
        # This should later be included in a for structure depending on the objective.
        bx_start = data_cube_Bp[0]
        by_start = np.multiply(-1,data_cube_Bt[0]) #need to multiply this for -1 at some point later on
        bz_start = data_cube_Br[0]
        bx_stop = data_cube_Bp[1]
        by_stop = np.multiply(-1,data_cube_Bt[1]) #need to multiply this for -1 at some point later on
        bz_stop = data_cube_Br[1]
        
        # Defining two variables to take initial and final time.
        try:
            # Testing if the registers are on the correct format.
            t1 = datetime.strptime(meta_cube_Bp[0]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
            t2 = datetime.strptime(meta_cube_Bp[1]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
            
        except ValueError:
            # Use t_rec if a value error is encountered.
            t1 = datetime.strptime(meta_cube_Bp[0]['t_rec'], "%Y.%m.%d_%H:%M:%S_TAI")
            t2 = datetime.strptime(meta_cube_Bp[1]['t_rec'], "%Y.%m.%d_%H:%M:%S_TAI")
            logging.debug('Value Error on t_obs, T rec used instead of t obs.')
            
        # Checking if the timestamp already exists.
        s = sql.select([Observations.id]).where(sql.and_(
                Observations.timestamp == t2,
                Observations.ar_id == ar_id))
        rp = session.execute(s)
        results = rp.fetchall()
        
        # Work on a new timestamp if the result is not yet on the database
        if results == []:
        
            # Calculating the time between the images in seconds.
            dt = (t2-t1).total_seconds()        
            
            # Calling do_dave4vm_and, which prepares pyDAVE4VM to be executed.
            magvm, vel4vm = do_dave4vm_and.do_dave4vm(dt,bx_stop, bx_start, by_stop,
                                                      by_start, bz_stop, bz_start,dx,
                                                      dy, window_size)
            
            # Checking if dave4vm was able to produce results.
            if vel4vm['solved'] is True:
                # Calculating the Poynting flux        
                En, Et, Es, int_En, int_Et, int_Es = poyntingflux(dx,
                                                                  magvm['bx'],
                                                                  magvm['by'],
                                                                  magvm['bz'],
                                                                  vel4vm['U0'],
                                                                  vel4vm['V0'],
                                                                  vel4vm['W0'])
                
                columnshape = np.shape(vel4vm['U0'])[0]
                
                # Logging.
                logging.info('The apperture problem could be solved, data processed.')
                # Prints to state progress.
                print('The apperture problem could be solved, data processed.')
            
            else:
                # Defaulting the Poynting flux and columnshape.
                En = Et = Es = int_En = int_Et = int_Es = columnshape = None
                
                # Logging.
                logging.info('The apperture problem could not be solved. ' +
                             f'({i}/{number_of_obs})')
                # Prints to state progress.
                print('The apperture problem could not be solved. ' + 
                      f'({i}/{number_of_obs})')
            
            # Here the actual data is led into the database by adding a new 
            # observation to it.
            try:
                new_obs = Observations(timestamp = t2,
                                       ar_id = ar_id,
                                       processed = vel4vm['solved'],
                                       columnshape = columnshape,
                                       d4vm_vx = ajuste(vel4vm['U0']),
                                       d4vm_vy = ajuste(vel4vm['V0']),
                                       d4vm_vz = ajuste(vel4vm['W0']), 
                                       mean_bx = ajuste(magvm['bx']),
                                       mean_by = ajuste(magvm['by']), 
                                       mean_bz = ajuste(magvm['bz']),
                                       poyn_En = ajuste(En), 
                                       poyn_Et = ajuste(Et), 
                                       poyn_Es = ajuste(Es),
                                       poyn_intEn = int_En,
                                       poyn_intEt = int_Et,
                                       poyn_intEs = int_Es)
                session.add(new_obs)
                session.commit()
                
            except AttributeError:
                session.rollback()
                logging.debug('Timestamp ' + str(t2) + ' not created.')
                print('Timestamp ' + str(t2) + ' not created.')
                
            else:
                logging.info('Timestamp ' + str(t2) + ' created. '  + 
                  f'({i}/{number_of_obs})')
                print('Timestamp ' + str(t2) + ' created. '  + 
                  f'({i}/{number_of_obs})')
                
            # Feedback.
            print(meta_cube_Bp[0]['t_obs'], ' Processed! ' + 
                  f'({i}/{number_of_obs})')
            
        else:
            logging.info('Timestamp ' + str(t2) + 
                         ' was already in the database.')
            print('Timestamp ' + str(t2) + 
                  ' was already in the database.')
    
    # Creating a timestamp for the analysis end.
    analysis_end = datetime.now()
    
    # Logging.
    logging.info('Analysis finished at: ' + str(analysis_end))
    logging.info('Total Execution time: ' + str(analysis_end - analysis_start))
    
    # Feedback.
    print('Active region ' + str(meta['noaa_ar']) + ' analysis completed.')
    print('Total Execution time: ', str(analysis_end - analysis_start))
    
    if delete_files == True:
        # Deleting files from the system.
        print('Deleting fits files...')
        
        try:
            # Deleting the folder with the fits files.
            shutil.rmtree(path)
            
        except OSError:
            # Feedback.
            print('Could not remove files.')
            # Logging.
            logging.debug('Files were not removed.')
            
        else:
            # Feedback.
            print('Files deleted.')
            # Logging.
            logging.info('Files deleted.')
    
    return
    
def execute_configs(path = None):
    '''
    This code will read multiple config files
    and execute the 'prepare' routine for each
    one of those files which will make the 
    analysis for each region featured on the
    file.
    '''
    # Checking if path to configs exists.
    if path is None:
        path = '/Users/andrechicrala/Downloads/configs/'
    
    # Searching for the config files paths.
    path = glob.glob(path+'*.ini')
    
    # Defining the path to move the config file to.
    path_to_move = path+'used/'
    
    # Iterating for each congif file.
    for config in path:
        print(f'Initiating the analysis for the file located ar: {config}')
        prepare(config_path = config)
        # Moving the config file to the used section.
        # rsplit will separate what is after and before the last slash.
        shutil.move(config, path_to_move + config.rsplit('/',1)[-1])
    
    # Feedback.    
    print('Finished =D')
    
    return

if __name__ == '__main__':
    '''
    test zone
    '''
    execute_configs()