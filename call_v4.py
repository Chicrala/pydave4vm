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
#importing the classes
from and_db.dbtest import Base, ActiveRegion, Observations, Dave4vm

def ajuste(data):
    '''
    Quick function to pass data in a numpy array 
    to string format. Somehow it wasn't working
    inside the main code.
    '''
    
    return(data.tostring())


def call_v4():
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
    
    #downloading data and returning the path
    try:
        path = downloaddata.downdrms(harpnum = harpnum,
                                     tstart = tstart,
                                     extent = extent,
                                     cadence = cadence)
        #logging
        logging.info('Downloads finished at: ' + str(datetime.now()))
        
    except RuntimeError:
        logging.debug('The download was not complete.')
        print('The download was not complete.')
    
    #Calling the cubitos2.py function to make the datacubes.
    #Don't forget to adapt the paths if necessary!
    data_cube_Br, data_cube_Bp, data_cube_Bt,\
    meta_cube_Bp = cubitos2.create_cube(path)
    
    #defining a dx and dy in km based on HMI resolution
    #used 1000 before!
    dx = (2*np.pi*6.955e8*meta_cube_Bp[0]['CDELT2']/360)/1000
    dy = dx
    
    #creating the sql engine:
    engine = create_engine(dbaddress)
    
    #declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    #binding the engine
    DBSession = sessionmaker(bind = engine)
    
    #the first session should create an item for the active region
    #using its noaa and harp numbers
    #starting session
    try:
        session = DBSession()
        new_ar = ActiveRegion(noaa_number = meta_cube_Bp[0]['noaa_ar'],
                              harp_number = meta_cube_Bp[0]['harpnum'])
        session.add(new_ar)
        session.commit()
        logging.info('AR ' + str(meta_cube_Bp[0]['harpnum']) + \
                     ' commited into the database.')
        #prints to state progress
        print('AR ' + str(meta_cube_Bp[0]['harpnum']) + \
                     ' commited into the database.')
        
    except AttributeError:
        logging.debug('AR not inserted into the database.')
        print('AR not inserted into the database.')
        
    #getting the id of the new active region
    try:
        session = DBSession()
        #creating the selec statement in the ActiveRegion table
        #filtering to get the key associated with the new
        #harp number
        s = sql.select([ActiveRegion]).where(
                ActiveRegion.harp_number == meta_cube_Bp[0]['harpnum'])
        #creating te result proxy
        rp = session.execute(s)
        #getting the results
        ar_id = rp.fetchall()[0][0]
        
        #colocar aqui codigo pra testar o tamanho de a
        
        session.commit()
        logging.info('AR ' + str(meta_cube_Bp[0]['harpnum']) + \
                     ' id is: ' + str(ar_id))
        #prints to state progress
        print('AR ' + str(meta_cube_Bp[0]['harpnum']) + \
                     ' id is: ' + str(ar_id))
        
    except AttributeError:
        
        #testing the two possible cases
        if len(ar_id) == 0:
            #logging
            logging.debug('No result for AR id.')
            print('No result for AR id.')
            
        else:
            #logging
            logging.debug('Inconsistent result for AR id.')
            print('Inconsistent result for AR id.')
            
    
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
        
        #adding a new observation to the database
        try:
            session = DBSession()
            new_obs = Observations(timestamp = t2, ar_id = ar_id)
            session.add(new_obs)
            session.commit()
            logging.info('Timestamp ' + str(t2) + ' created.')
            print('Timestamp ' + str(t2) + ' created.')
            
        except AttributeError:
            logging.debug('Timestamp ' + str(t2) + ' not created.')
            print('Timestamp ' + str(t2) + ' not created.')
            
        
        
        #getting the observation id
        #getting the id of the new active region
        try:
            session = DBSession()
            #creating the selec statement in the ActiveRegion table
            #filtering to get the key associated with the new
            #harp number
            s = sql.select([Observations]).where(
                    Observations.timestamp == t2)
            #creating te result proxy
            rp = session.execute(s)
            #getting the results
            obs_id = rp.fetchall()[0][0]
            
            #colocar aqui codigo pra testar o tamanho de a
            
            session.commit()
            
            logging.info('Observation ' + str(t2) + \
                         ' id is: ' + str(obs_id))
            #prints to state progress
            print('Observation ' + str(t2) + \
                         ' id is: ' + str(obs_id))
            
        except AttributeError:
            
            #testing the two possible cases
            if len(obs_id) == 0:
                #logging
                logging.debug('No result for obs '+ str(t2)+ ' id.')
                print('No result for obs '+ str(t2)+ ' id.')
                
            else:
                #logging
                logging.debug('Inconsistent result for obs '+ str(t2)+ ' id.')
                print('Inconsistent result for obs '+ str(t2)+ ' id.')
            
        #prints to state progress
        print('Timestamp', meta_cube_Bp[i+1]['t_obs'], 'created.')
        
        
        #Calling do_dave4vm_and 
        magvm, vel4vm = do_dave4vm_and.do_dave4vm(dt,bx_stop, bx_start, by_stop,
                                                  by_start, bz_stop, bz_start,dx,
                                                  dy, window_size)
        
        #calculating the Poynting flux        
        En, Et, Es, int_En, int_Et, int_Es = poyntingflux(dx,
                                                          magvm['bx'],
                                                          magvm['by'],
                                                          magvm['bz'],
                                                          vel4vm['U0'],
                                                          vel4vm['V0'],
                                                          vel4vm['W0'])
        
        #here the actual data is led into the database
        try:
            session = DBSession()
            new_dave4vm = Dave4vm(columnshape = np.shape(vel4vm['U0'])[0],
                                  vx = ajuste(vel4vm['U0']),
                                  vy = ajuste(vel4vm['V0']),
                                  vz = ajuste(vel4vm['W0']), 
                                  bx = ajuste(magvm['bx']),
                                  by = ajuste(magvm['by']), 
                                  bz = ajuste(magvm['bz']),
                                  En = ajuste(En), 
                                  Et = ajuste(Et), 
                                  Es = ajuste(Es),
                                  intEn = int_En,
                                  intEt = int_Et,
                                  intEs = int_Es,
                                  obs_id = obs_id)
            session.add(new_dave4vm)
            session.commit()
            
            #making the log
            logging.info('Observation ' + str(obs_id) + \
                     ' data inserted into the database.')
            #prints to state progress
            print('Observation ' + str(obs_id) + \
                     ' data inserted into the database.')
            
        except AttributeError:
            #making the log
            logging.debug('Data not inserted into the database.')
            print('Data not inserted into the database.')
            
        #feedback
        print(meta_cube_Bp[i]['t_obs'], ' Processed! =D')
    
    #creating a timestamp for the analysis end
    analysis_end = datetime.now()
    
    #logging
    logging.info('Analysis finished at: ' + str(analysis_end))
    logging.info('Total Execution time: ' + str(analysis_end - analysis_start))
    
    #printing
    print('Active region ' + str(meta_cube_Bp[0]['noaa_ar']) + 'analysis completed.')
    print('Total Execution time: ', str(analysis_end - analysis_start))
    
    #delete files
    #shutil.rmtree() will delete a directory and all its contents.
    print('Deleting fits files...')
    
    #using a try/except statement to remove the files
    try:
        #deleting the folder with the fits files
        shutil.rmtree(path)
        #feedback
        print('Files deleted.')
        #logging info
        logging.info('Files deleted.')
        
    except OSError:
        #printing that an error occured
        print('Could not remove files.')
        #logging the error
        logging.debug('Files were not removed.')
    
    return()


if __name__ == "__main__":
    '''
    The testing zone
    '''
    call_v4()
    

    
        
        
