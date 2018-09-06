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
    
    #creating a timestamp for the analysis start:
    analysis_start = datetime.now()
    
    #definning the path for the config file
    #config_path = glob.glob('/Users/andrechicrala/Downloads/configs/*.ini')
    
    #reading the config file
    harpnum, tstart, extent, cadence, dbaddress,\
    window_size, = myconfig.readconfig(config_path)
    
    #creating the log file
    logging.basicConfig(filename = str(harpnum)+'.log',
                        level=logging.DEBUG)
    
    #logging
    logging.info('Analysis started at: ' + str(analysis_start))
    
    #checking if data is already in the disk
    if downloaded == None:
        
        #check in the standard path if file exists
        std_path = '/Users/andrechicrala/Downloads/'+ str(harpnum)+'/'
        #if it don't, download
        if os.path.exists(std_path) != True:
        
            #downloading data and returning the path
            try:
                path = downloaddata.downdrms(harpnum = harpnum,
                                             tstart = tstart,
                                             extent = extent,
                                             cadence = cadence)
                
                
            except RuntimeError:
                logging.debug('The download was not complete.')
                print('The download was not complete.')
                
            #add the log if try is sucessfull 
            else:
                #logging
                logging.info('Downloads finished at: ' + str(datetime.now()))
                
        #if it does use the files there
        else:
            path = std_path
    
    #assigning the path to the files        
    else:
        
        #checking if the path exists
        while os.path.exists(downloaded) != True:
            #inputing the path
            downloaded = str(input('Inform the path to the downloaded files enclosing folder: '))
        
        #logging
        logging.info('The files were already saved in the disk.')
        print('The files were already saved in the disk.')
        
        #assigning the path
        path = downloaded
        
    #checking how many files are inside the directory
    number_of_files = len(fnmatch.filter(os.listdir(path),'*.fits'))
    
    #and taking the results to the log.
    logging.info('There are ' + str(number_of_files) + 
                ' .fits files saved in the disk.')
    print('There are ' + str(number_of_files) + 
                ' .fits files saved in the disk.')
    
    #deleting variable
    del number_of_files
                    
    #Checking if there are 3 files for each
    #magnetic field component
    Br_unique, Bt_unique, Bp_unique = check_fits.check_fits(path)
    
    #logging any missing files
    if Br_unique == [] and Bt_unique == [] and Bp_unique == []:
        logging.info('There are no missing files')
        print('There are no missing files.')
        
    else:
        logging.info('Listing the removed elements: ')
        print('Listing the removed elements: ')
        #looping over each list to tell which
        #elements were missing
        for item in Br_unique:
            logging.info(f'{item}')
            print(f'{item}')
            
        for item in Bt_unique:
            logging.info(f'{item}')
            print(f'{item}')
            
        for item in Bp_unique:
            logging.info(f'{item}')
            print(f'{item}')
    
    #deleting those lists
    del Br_unique, Bt_unique, Bp_unique
    
    #checking the number of observations
    number_of_obs = int(len(fnmatch.filter(os.listdir(path),'*.fits'))/3)
    
    #taking the information from one of the files
    meta = sunpy.map.Map(path + os.listdir(path)[0]).meta
    
    #defining a dx and dy in km based on HMI resolution
    #used 1000 before!
    dx = (2*np.pi*6.955e8*meta['CDELT2']/360)/1000
    dy = dx
    
    #creating the sql engine:
    engine = create_engine(dbaddress, pool_pre_ping=True)
    
    #declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    #binding the engine
    DBSession = sessionmaker(bind = engine)
    #creating the session
    session = DBSession()

    #check if stamp exist to keep completing it
    s = sql.select([ActiveRegion]).where(
                ActiveRegion.harp_number == meta['harpnum'])
    
    #using the result proxy
    rp = session.execute(s)
    
    #fetching the results
    AR = rp.fetchall()
    
    #if the AR isn't there yet, insert it into
    #the database.
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
            logging.debug('AR not inserted into the database.')
            print('AR not inserted into the database.')
            
        else:
            #checking the ar_id
            #check if stamp exist to keep completing it
            s = sql.select([ActiveRegion]).where(
                        ActiveRegion.harp_number == meta['harpnum'])
            
            #using the result proxy
            rp = session.execute(s)
            
            #fetching the results
            AR = rp.fetchall()
            
            #assigning the ar number
            ar_id = AR[0][0]
            
            #checking if the result is an int
            if type(ar_id) != int:
                #logging
                logging.debug('Inconsistent type for AR id.')
                print('Inconsistent type for AR id.')
                print('Abort Mission!')
                sys.exit('Exiting')
            
            
            logging.info('AR ' + str(meta['harpnum']) + \
                         ' commited into the database. New AR id: ' + \
                         str(ar_id))
            #prints to state progress
            print('AR ' + str(meta['harpnum']) + \
                         ' commited into the database. New AR id: ' + \
                         str(ar_id))
            
        
    else:
        #printing which is the table positioning
        logging.info(f'The Active Region {AR[0][1],AR[0][2]} is already in the '
              f'database with the id: {AR[0][0]}')
        
        print(f'The Active Region {AR[0][1],AR[0][2]} is already in the '
              f'database with the id: {AR[0][0]}')
        
        #assigning the ar number
        ar_id = AR[0][0]
        
        #checking if the result is an int
        if type(ar_id) != int:
            #logging
            logging.debug('Inconsistent type for AR id.')
            print('Inconsistent type for AR id.')
            print('Abort Mission!')
            sys.exit('Exiting')
    
    #looping over all the datacubes
    #note that all of them should have
    #the same dimensions which is already
    #standard for the cea data
    for i in range(len(glob.glob(path+'*.Bp.fits'))-1):
        
        #Calling the cubitos2.py function to make the datacubes.
        data_cube_Br, data_cube_Bp, data_cube_Bt,\
        meta_cube_Bp = cubitos3.create_cube(path, i)
    
        #Defining the start and end points based on the datacubes.
        #This should later be included in a for structure depending on the objective.
        bx_start = data_cube_Bp[0]
        by_start = np.multiply(-1,data_cube_Bt[0]) #need to multiply this for -1 at some point later on
        bz_start = data_cube_Br[0]
        bx_stop = data_cube_Bp[1]
        by_stop = np.multiply(-1,data_cube_Bt[1]) #need to multiply this for -1 at some point later on
        bz_stop = data_cube_Br[1]
        
        #defining two variables to take initial and final time
        try:
            #testing if the registers are on the correct
            #format
            t1 = datetime.strptime(meta_cube_Bp[0]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
            t2 = datetime.strptime(meta_cube_Bp[1]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
            
        except ValueError:
            #use t_rec instead
            t1 = datetime.strptime(meta_cube_Bp[0]['t_rec'], "%Y.%m.%d_%H:%M:%S_TAI")
            t2 = datetime.strptime(meta_cube_Bp[1]['t_rec'], "%Y.%m.%d_%H:%M:%S_TAI")
            logging.debug('Value Error on t_obs, T rec used instead of t obs.')
            
        #checking if the timestamp already exists
        s = sql.select([Observations.id]).where(sql.and_(
                Observations.timestamp == t2,
                Observations.ar_id == ar_id))
        rp = session.execute(s)
        results = rp.fetchall()
        
        #work on a new timestamp if the result
        #is not yet on the database
        if results == []:
        
            #calculating the time between the images in seconds
            dt = (t2-t1).total_seconds()        
            
            #Calling do_dave4vm_and 
            magvm, vel4vm = do_dave4vm_and.do_dave4vm(dt,bx_stop, bx_start, by_stop,
                                                      by_start, bz_stop, bz_start,dx,
                                                      dy, window_size)
            
            #checking if dave4vm has a null element
            if vel4vm['solved'] is True:
                #calculating the Poynting flux        
                En, Et, Es, int_En, int_Et, int_Es = poyntingflux(dx,
                                                                  magvm['bx'],
                                                                  magvm['by'],
                                                                  magvm['bz'],
                                                                  vel4vm['U0'],
                                                                  vel4vm['V0'],
                                                                  vel4vm['W0'])
                
                columnshape = np.shape(vel4vm['U0'])[0]
                
                #logging
                logging.info('The apperture problem could be solved, data processed.')
                #prints to state progress
                print('The apperture problem could be solved, data processed.')
            
            else:
                #defaulting the Poynting flux and columnshape
                En = Et = Es = int_En = int_Et = int_Es = columnshape = None
                
                #logging
                logging.info('The apperture problem could not be solved. ' +
                             f'({i}/{number_of_obs})')
                #prints to state progress
                print('The apperture problem could not be solved. ' + 
                      f'({i}/{number_of_obs})')
            
            #here the actual data is led into the database
            #adding a new observation to the database
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
                logging.debug('Timestamp ' + str(t2) + ' not created.')
                print('Timestamp ' + str(t2) + ' not created.')
                
            else:
                logging.info('Timestamp ' + str(t2) + ' created. '  + 
                  f'({i}/{number_of_obs})')
                print('Timestamp ' + str(t2) + ' created. '  + 
                  f'({i}/{number_of_obs})')
                
            #feedback
            print(meta_cube_Bp[0]['t_obs'], ' Processed! ' + 
                  f'({i}/{number_of_obs})')
            
        else:
            logging.info('Timestamp ' + str(t2) + 
                         ' was already in the database.')
            print('Timestamp ' + str(t2) + 
                  ' was already in the database.')
    
    #creating a timestamp for the analysis end
    analysis_end = datetime.now()
    
    #logging
    logging.info('Analysis finished at: ' + str(analysis_end))
    logging.info('Total Execution time: ' + str(analysis_end - analysis_start))
    
    #printing
    print('Active region ' + str(meta['noaa_ar']) + ' analysis completed.')
    print('Total Execution time: ', str(analysis_end - analysis_start))
    
    if delete_files == True:
        #delete files
        #shutil.rmtree() will delete a directory and all its contents.
        print('Deleting fits files...')
        
        #using a try/except statement to remove the files
        try:
            #deleting the folder with the fits files
            shutil.rmtree(path)
            
        except OSError:
            #printing that an error occured
            print('Could not remove files.')
            #logging the error
            logging.debug('Files were not removed.')
        
        #logging
        else:
            #feedback
            print('Files deleted.')
            #logging info
            logging.info('Files deleted.')
    
    return
    
def execute_configs():
    '''
    This code will read multiple config files
    and execute the 'prepare' routine for each
    one of those files which will make the 
    analysis for each region featured on the
    file.
    '''
    
    #searching for the config files paths
    path = glob.glob('/Users/andrechicrala/Downloads/configs/*.ini')
    #defining the path to move the config file to
    path_to_move = '/Users/andrechicrala/Downloads/configs/used/'
    
    #iterating for each file
    for config in path:
        print(f'Initiating the analysis for the file located ar: {config}')
        prepare(config_path = config)
        #Moving the config file to the used section
        #rsplit will separate what is after and before
        #the last slash
        shutil.move(config, path_to_move + config.rsplit('/',1)[-1])
        
    print('Finished =D')
    
    return

if __name__ == '__main__':
    
    configs()