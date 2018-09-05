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


use con and get like here:
    https://gist.github.com/maedoc/b5b3cd91aaa59ec573f9
    
    

@author: andrechicrala
"""

#importing basic packages
import numpy as np
from datetime import datetime
#calling my set of packages
from pydave4vm import cubitos2
from pydave4vm import do_dave4vm_and
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

def ajuste(data):
    '''
    Quick function to pass data in a numpy array 
    to string format. Somehow it wasn't working
    inside the main code.
    '''
    
    return(data.tostring())


def call_v4(downloaded = None, delete_files = None):
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
    config_path = glob.glob('/Users/andrechicrala/Downloads/configs/*.ini')
    
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
    #and taking the results to the log.
    logging.info('There are ' + str(len(fnmatch.filter(os.listdir(downloaded), 
                                                      '*.fits'))) + 
                ' .fits files saved in the disk.')
    print('There are ' + str(len(fnmatch.filter(os.listdir(downloaded), 
                                                      '*.fits'))) + 
                ' .fits files saved in the disk.')
    
    #Calling the cubitos2.py function to make the datacubes.
    #Don't forget to adapt the paths if necessary!
    data_cube_Br, data_cube_Bp, data_cube_Bt,\
    meta_cube_Bp = cubitos2.create_cube(path)
    
    #defining a dx and dy in km based on HMI resolution
    #used 1000 before!
    dx = (2*np.pi*6.955e8*meta_cube_Bp[0]['CDELT2']/360)/1000
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
                ActiveRegion.harp_number == meta_cube_Bp[0]['harpnum'])
    
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
            session = DBSession()
            new_ar = ActiveRegion(noaa_number = meta_cube_Bp[0]['noaa_ar'],
                                  harp_number = meta_cube_Bp[0]['harpnum'])
            session.add(new_ar)
            session.commit()
            
        #adding the atribute exception    
        except AttributeError:
            logging.debug('AR not inserted into the database.')
            print('AR not inserted into the database.')
            
        #connection lost error
        #http://docs.sqlalchemy.org/en/latest/errors.html#error-rvf5        
        #except sql.exc.InterfaceError:
            #logging
            #logging.info('Connection with the database lost.')
            #prints to state progress
            #print('Connection with the database lost.')
            #stopping the code
            #_ = input('What to do? Continue (c) or quit (q)?')
            
            #if _ == 'q':
            #    sys.exit('Exiting')
        
        #if try works, add it to the log
        else:
            logging.info('AR ' + str(meta_cube_Bp[0]['harpnum']) + \
                         ' commited into the database.')
            #prints to state progress
            print('AR ' + str(meta_cube_Bp[0]['harpnum']) + \
                         ' commited into the database.')
            
        
    else:
        #printing which is the table positioning
        logging.info(f'The Active Region {AR[0][1],AR[0][2]} is already in the '
              f'database with the id: {AR[0][0]}')
        
        print(f'The Active Region {AR[0][1],AR[0][2]} is already in the '
              f'database with the id: {AR[0][0]}')
        
        #testing
        ar_id = AR[0][0]
        
        #checking if the result is an int
        if type(ar_id) != int:
            #logging
            logging.debug('Inconsistent type for AR id.')
            print('Inconsistent type for AR id.')
            print('Abort Mission!')
            sys.exit('Exiting')
            
        
        else:
            #logging
            logging.debug('Inconsistent result for AR id.')
            print('Inconsistent result for AR id.')
    
    #connection lost error
    #http://docs.sqlalchemy.org/en/latest/errors.html#error-rvf5        
    #except sql.exc.InterfaceError:
        #logging
    #    logging.info('Connection with the database lost.')
        #prints to state progress
    #    print('Connection with the database lost.')
        #stopping the code
    #    _ = input('What to do? Continue (c) or quit (q)?')
        
    #    if _ == 'q':
    #        sys.exit('Exiting')
            
    #looping over all the datacubes
    #note that all of them should have
    #the same dimensions
    for i in range(len(data_cube_Br)-1):
    
        #Defining the start and end points based on the datacubes.
        #This should later be included in a for structure depending on the objective.
        bx_start = data_cube_Bp[i]
        by_start = np.multiply(-1,data_cube_Bt[i]) #need to multiply this for -1 at some point later on
        bz_start = data_cube_Br[i]
        bx_stop = data_cube_Bp[i+1]
        by_stop = np.multiply(-1,data_cube_Bt[i+1]) #need to multiply this for -1 at some point later on
        bz_stop = data_cube_Br[i+1]
        
        #defining two variables to take initial and final time
        t1 = datetime.strptime(meta_cube_Bp[i]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
        t2 = datetime.strptime(meta_cube_Bp[i+1]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
        
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
            logging.info('The apperture problem could not be solved.')
            #prints to state progress
            print('The apperture problem could not be solved.')
        
        #here the actual data is led into the database
        #adding a new observation to the database
        try:
            session = DBSession()
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
            logging.info('Timestamp ' + str(t2) + ' created.')
            print('Timestamp ' + str(t2) + ' created.')
            
        #feedback
        print(meta_cube_Bp[i]['t_obs'], ' Processed! =D')
    
    #creating a timestamp for the analysis end
    analysis_end = datetime.now()
    
    #logging
    logging.info('Analysis finished at: ' + str(analysis_end))
    logging.info('Total Execution time: ' + str(analysis_end - analysis_start))
    
    #printing
    print('Active region ' + str(meta_cube_Bp[0]['noaa_ar']) + ' analysis completed.')
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
            
    
    return()