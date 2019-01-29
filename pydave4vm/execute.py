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

# Importing packages to perform operations in the code.
import numpy as np
from datetime import datetime
import logging
import fnmatch
import sunpy
import sunpy.map
import json

# Importing system related packages.
import glob
import shutil
import sys
import os

# Calling the package that will execute PyDAVE4VM.
from pydave4vm import do_dave4vm

# Importing the addons for PyDAVE4VM.
from pydave4vm.addons import myconfig, stdconfig, neutralline, cubitos3, check_fits, swpc_db, swpcparser, downloaddata
from pydave4vm.addons.poyntingflux import poyntingflux

# Importing the packages to operate with the database.
import sqlalchemy as sql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydave4vm.addons.maindb import ActiveRegion, Observations, Events, Morphology

def ajuste(data):
    '''
    Quick function to pass data in a numpy array 
    to string format. Somehow it wasn't working
    inside the main code.
    '''
    
    return(data.tostring())


def prepare(config_path, os_, downloaded = None, delete_files = None):
    '''
    This is the pre-routine to execute pydave4vm.
    Here the following steps are taken:
        
        - The parameters are fetch from an external file;
        - Data is downloaded using drms to query JSOC;
        - The fits are organized into datacubes;
        - Data is inserted into the do_dave4vm module;
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
                
        # If it does use the files there.
        else:
            path = std_path
            
            # Checking for missing files within the path.
            missing_files = downloaddata.check_missing_files(harpnum=harpnum, 
                                                             directory=std_path,
                                                             tstart=tstart,
                                                             extent=extent,
                                                             cadence=cadence)
            
            # Reporting missing files.
            if missing_files != []:
                print(f'Missing files: {missing_files}')
                logging.debug(f'Missing files: {missing_files}')
    
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
    
    # Taking the header information from one of the files.
    meta = sunpy.map.Map(path + os.listdir(path)[0]).meta
    
    # Defining a dx and dy in km based on HMI resolution.
    dx = (2*np.pi*6.955e8*meta['CDELT2']/360)/1000
    dy = dx
    
    # Checking the length of the image in the y-axis.
    columnshape = np.shape(sunpy.map.Map(path + os.listdir(path)[0]).data)[0]
    rowshape = np.shape(sunpy.map.Map(path + os.listdir(path)[0]).data)[1]
    
    ###########################################################################
    # Starting the database session.
    ################################
    # Creating the sql engine.
    engine = create_engine(dbaddress)
    
    # Binding the engine.
    DBSession = sessionmaker(bind=engine)
    # Creating the session.
    session = DBSession()
    ###########################################################################
    # Populating the ActiveRegion table.
    ####################################
    # Check if stamp exist to keep completing it.
    s = sql.select([ActiveRegion]).where(
                ActiveRegion.harp_number == harpnum)
    
    # Using the result proxy to query the results.
    rp = session.execute(s)
    
    # Fetching all the results.
    AR = rp.fetchall()
    
    #If the AR isn't there yet, insert it into the database.
    if AR == []:
        
        # The first session should create an item for the ActiveRegion table.
        # Using its noaa and harp numbers. Starting session.
        try:
            new_ar = ActiveRegion(harp_number=harpnum,
                                  columnshape=columnshape,
                                  rowshape=rowshape)
            session.add(new_ar)
            session.commit()
            
        # Adding the atribute exception.
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
                        ActiveRegion.harp_number == harpnum)
            
            # Quqerying and fetching the results
            rp = session.execute(s)
            AR = rp.fetchall()
            
            # Assigning the ar number to a variable.
            ar_id = AR[0][0]
            
            # Checking if the result is an int.
            if type(ar_id) != int:
                # Logging.
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
        
        # Assigning the ar number.
        ar_id = AR[0][0]
        
        # Checking if the result is an int.
        if type(ar_id) != int:
            # Logging.
            logging.debug('Inconsistent type for AR id.')
            print('Inconsistent type for AR id.')
            print('Abort Mission!')
            sys.exit('Exiting')
            
    # Creating an empty to store all the NOAA numbers.
    noaa_numbers = []
    
    ###########################################################################
    # Looping over all the datacubes. Note that all of them should have the 
    # same dimensions which is already standard for the cea data.
    for i in range(len(glob.glob(path+'*.Bp.fits'))-1):
        #######################################################################
        # Data preparation.
        ###################
        #Calling the function to make the datacubes.
        data_cube_Br, data_cube_Bp, data_cube_Bt,\
        meta_cube_Bp = cubitos3.create_cube(path, i)
    
        # Defining the start and end points based on the datacubes.
        # This should later be included in a for structure depending on the objective.
        bx_start = data_cube_Bp[0]
        by_start = np.multiply(-1,data_cube_Bt[0])
        bz_start = data_cube_Br[0]
        bx_stop = data_cube_Bp[1]
        by_stop = np.multiply(-1,data_cube_Bt[1])
        bz_stop = data_cube_Br[1]
        
        # Defining two variables to take initial and final time.
        try:
            # Testing if the registers are on the correct format.
            t1 = datetime.strptime(meta_cube_Bp[0]['date-obs'], "%Y-%m-%dT%H:%M:%S.%f")
            t2 = datetime.strptime(meta_cube_Bp[1]['date-obs'], "%Y-%m-%dT%H:%M:%S.%f")
            
        except ValueError:
            # Use t_rec if a value error is encountered.
            t1 = datetime.strptime(meta_cube_Bp[0]['t_rec'], "%Y.%m.%d_%H:%M:%S_TAI")
            t2 = datetime.strptime(meta_cube_Bp[1]['t_rec'], "%Y.%m.%d_%H:%M:%S_TAI")
            print('Value Error on date-obs, t_rec used instead of date-obs.')
            logging.debug('Value Error on date-obs, t_rec used instead of date-obs.')
            
        # Checking if the timedelta is consistent.
        if abs((t2-t1).seconds-720) > 7:
            print('Time delta deviated by more than 1%. \n ',
                  f't1: {t1} \n',
                  f't2: {t2} \n',
                  f'Deltat: {(t2-t1).seconds} \n')
            logging.debug('Time delta deviated by more than 1%. \n ',
                          f't1: {t1} \n',
                          f't2: {t2} \n',
                          f'Deltat: {(t2-t1).seconds} \n')
            continue
            
        # Checking if the shape is consistent among the observations.
        if np.shape(bx_start) != np.shape(bx_stop):
            print(f'Shape not consistent. bx_start({t1}): {np.shape(bx_start)}, bx_stop({t2}): {np.shape(bx_stop)}')
            logging.debug(f'Shape not consistent. bx_start({t1}): {np.shape(bx_start)}, bx_stop({t2}): {np.shape(bx_stop)}')
            # Go to the next step.
            continue
            
        # Checking if the timestamp already exists.
        check = session.query(sql.exists().where(sql.and_(Observations.ar_id == ar_id,
                                                          Observations.timestamp_int == int(t2.strftime('%Y%m%d%H%M%S'))))).scalar()
        
        #######################################################################
        # Obtaining the velocities with PyDAVE4VM.
        ##########################################
        # Work on a new timestamp if the result is not yet on the database
        if check is False:
        
            # Calculating the time between the images in seconds.
            dt = (t2-t1).total_seconds()        
            
            # Calling do_dave4vm, which prepares pyDAVE4VM to be executed.
            magvm, vel4vm = do_dave4vm.do_dave4vm(dt,bx_stop, bx_start, by_stop,
                                                      by_start, bz_stop, bz_start,dx,
                                                      dy, window_size)
            
            # Checking if dave4vm was able to produce results.
            if vel4vm['solved'] is True:
                # Calculating the Poynting flux        
                Sn, St, Ss, int_Sn, int_St, int_Ss = poyntingflux(dx,
                                                                  magvm['bx'],
                                                                  magvm['by'],
                                                                  magvm['bz'],
                                                                  vel4vm['U0'],
                                                                  vel4vm['V0'],
                                                                  vel4vm['W0'])
                
                columnshape = np.shape(vel4vm['U0'])[0]
                
                ###############################################################
                # Integration around the PILS.
                ##############################
                # Creating the PIL gaussian broadening mask.
                pil_gb_map = neutralline.PIL(magvm['bz'], gaussian=True)
                
                # Testing if the PIL actually exists.
                if np.sum(pil_gb_map) > 0.1:
                    # Integrating the Poynting flux components along the PIL.
                    int_PIL_Sn = np.sum(np.multiply(Sn,pil_gb_map))
                    int_PIL_pos_Sn = np.sum(np.multiply(np.multiply(Sn,(Sn > 0).astype(float)),
                                                        pil_gb_map))
                    int_PIL_neg_Sn = np.sum(np.multiply(np.multiply(Sn,(Sn < 0).astype(float)),
                                                        pil_gb_map))
                    
                    int_PIL_St = np.sum(np.multiply(St,pil_gb_map))
                    int_PIL_pos_St = np.sum(np.multiply(np.multiply(St,(St > 0).astype(float)),
                                                        pil_gb_map))
                    int_PIL_neg_St = np.sum(np.multiply(np.multiply(St,(St < 0).astype(float)),
                                                        pil_gb_map))
                    
                    int_PIL_Ss = np.sum(np.multiply(Ss,pil_gb_map))
                    int_PIL_pos_Ss = np.sum(np.multiply(np.multiply(Ss,(Ss > 0).astype(float)),
                                                        pil_gb_map))
                    int_PIL_neg_Ss = np.sum(np.multiply(np.multiply(Ss,(Ss < 0).astype(float)),
                                                        pil_gb_map))
                    
                    # Calculating Schrijver's R.
                    logR = np.log10(np.sum(np.absolute(np.multiply(magvm['bz'],
                                                                   pil_gb_map))))
                # Logging.
                logging.info('The apperture problem could be solved, data processed.')
                # Prints to state progress.
                print('The apperture problem could be solved, data processed.')
            
            else:
                ###############################################################
                # Poynting flux calculation.
                ############################
                # Defaulting the Poynting flux and columnshape.
                Sn = St = Ss = int_Sn = int_St = int_Ss = columnshape = logR = None
                int_PIL_Sn = int_PIL_pos_Sn = int_PIL_neg_Sn = None
                int_PIL_St = int_PIL_pos_St = int_PIL_neg_St = None
                int_PIL_Ss = int_PIL_pos_Ss = int_PIL_neg_Ss = None
                
                # Logging.
                logging.info('The apperture problem could not be solved. ' +
                             f'({i}/{number_of_obs})')
                # Prints to state progress.
                print('The apperture problem could not be solved. ' + 
                      f'({i}/{number_of_obs})')
            ###################################################################
            # Finding the NOAA numbers of these observations.
            #################################################
            # Calling the function that does it and placing the NOAA numbers
            # in numerical order.
            noaa_number = sorted(swpc_db.find_noaa_number(meta_cube_Bp[1]))
            
            # Appending the NOAA numbers to the overall list.
            for thing in noaa_number:
                if thing not in noaa_numbers:
                    noaa_numbers.append(thing)
            
            # Filling all the available slots.
            while len(noaa_number) < 3:
                noaa_number.append(None)
            
            ###################################################################
            # Data insertion.
            #################
            # Here the actual data is led into the database by adding a new 
            # observation to it.
            try:
                new_obs = Observations(timestamp_dt=t2,
                                       timestamp_int=int(t2.strftime('%Y%m%d%H%M%S')),
                                       deltat=dt,
                                       ar_id=ar_id,
                                       d4vm_vx=ajuste(vel4vm['U0']),
                                       d4vm_vy=ajuste(vel4vm['V0']),
                                       d4vm_vz=ajuste(vel4vm['W0']), 
                                       mean_bx=ajuste(magvm['bx']),
                                       mean_by=ajuste(magvm['by']), 
                                       mean_bz=ajuste(magvm['bz']),
                                       poyn_Sn=ajuste(Sn), 
                                       poyn_St=ajuste(St), 
                                       poyn_Ss=ajuste(Ss),
                                       int_Sn=int_Sn,
                                       int_St=int_St,
                                       int_Ss=int_Ss,
                                       int_PIL_Sn=int_PIL_Sn,
                                       int_PIL_pos_Sn=int_PIL_pos_Sn,
                                       int_PIL_neg_Sn=int_PIL_neg_Sn,
                                       int_PIL_St=int_PIL_St,
                                       int_PIL_pos_St=int_PIL_pos_St,
                                       int_PIL_neg_St=int_PIL_neg_St,
                                       int_PIL_Ss=int_PIL_Ss,
                                       int_PIL_pos_Ss=int_PIL_pos_Ss,
                                       int_PIL_neg_Ss=int_PIL_neg_Ss,
                                       logR=logR,
                                       hmi_meta_data=json.dumps(meta_cube_Bp[1]),
                                       noaa_number1=noaa_number[0],
                                       noaa_number2=noaa_number[1],
                                       noaa_number3=noaa_number[2])
                
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
            continue
    ###########################################################################
    # Creating a timestamp for the analysis end.
    observations_end = datetime.now()
    
    # Logging.
    logging.info('Observation table analysis finished at: ' + str(observations_end))
    ###########################################################################
    # Populating the Morphology and Events tables.
    ##############################################
    # Separating the unique NOAA numbers.
    noaa_numbers = list(sorted(set(noaa_numbers)))
    
    # Getting all the morphology entries for this AR.
    morphologies = swpcparser.morphology_seeker(None,noaa_numbers)
    
    # Flatenning the results into a list and taking all the results 
    # into the database.
    for key in sorted(morphologies.keys()):
        # Checking if this morphology already exists within the db.
        check = session.query(sql.exists().where(sql.and_(Morphology.noaa_number == morphologies[key]['noaa_number'],
                                                          Morphology.daystamp_int == morphologies[key]['daystamp_int']))).scalar()
        
        if check is True:
            print(f'Morphology {key} ALREADY inserted.')
            logging.info(f'Morphology {key} ALREADY inserted.')
            continue
        
        # Creating a new entry for the Morphology table.
        new_morph = Morphology(ar_id=ar_id,
                               noaa_number=morphologies[key]['noaa_number'],
                               mcintosh=morphologies[key]['mcintosh'],
                               hale=morphologies[key]['hale'],
                               daystamp_dt=morphologies[key]['daystamp_dt'],
                               daystamp_int=morphologies[key]['daystamp_int'],
                               latitude=morphologies[key]['latitude'],
                               longitude=morphologies[key]['longitude'],
                               LL=morphologies[key]['LL'],
                               Lo=morphologies[key]['Lo'],
                               NN=morphologies[key]['NN'],
                               area=morphologies[key]['area'])
        
        try:
            session.add(new_morph)
            session.commit()
            
        except ValueError:
            session.rollback()
            print(f'Morphology {key} NOT inserted.')
            logging.info(f'Morphology {key} NOT inserted.')
        
        else:
            print(f'Morphology {key} inserted.')
            logging.info(f'Morphology {key} inserted.')
        
    # Doing the same for the Events.
    events = swpcparser.event_seeker(None,noaa_numbers)
    
    # Flatenning the results into a list and taking all the results 
    # into the database.
    for key in sorted(events.keys()):
        # Checking if this morphology already exists within the db.
        check = session.query(sql.exists().where(Events.event_number == events[key]['Event'])).scalar()
        
        if check is True:
            print(f'Event {key} ALREADY inserted.')
            logging.info(f'Event {key} ALREADY inserted.')
            continue
        
        # Creating a new entry for the Morphology table.
        new_eve = Events(ar_id=ar_id,
                           flareclass=events[key]['Class'],
                           event_begin_dt=events[key]['Begin'],
                           event_max_dt=events[key]['Max'],
                           event_end_dt=events[key]['End'],
                           event_begin_int=events[key]['Beginint'],
                           event_max_int=events[key]['Maxint'],
                           event_end_int=events[key]['Endint'],
                           noaa_number=events[key]['noaa_number'],
                           event_number=events[key]['Event'],
                           daystamp_dt=events[key]['daystamp_dt'],
                           daystamp_int=events[key]['daystamp_int'])
        
        try:
            session.add(new_eve)
            session.commit()
            
        except ValueError:
            session.rollback()
            print(f'Events {key} NOT inserted.')
            logging.info(f'Events {key} NOT inserted.')
        
        else:
            print(f'Events {key} inserted.')
            logging.info(f'Events {key} inserted.')
            
    ###########################################################################
    # Updating the NOAA number and max hale class entries for the set.
    ##################################################################
    # Searching for the max hale class of the ARs.
    max_hale_classes = swpc_db.find_max_hale_class(noaa_numbers)
    
    # Filling the available slots.
    while len(noaa_numbers) <3:
        noaa_numbers.append(None)
        
    while len(max_hale_classes) <3:
        max_hale_classes.append(None)
    
    # Updating the values.    
    query = session.query(ActiveRegion)
    query = query.filter(ActiveRegion.AR_id == ar_id)
    query.update({ActiveRegion.noaa_number1: noaa_numbers[0],
                  ActiveRegion.noaa_number2: noaa_numbers[1],
                  ActiveRegion.noaa_number3: noaa_numbers[2],
                  ActiveRegion.max_hale_class1: max_hale_classes[0],
                  ActiveRegion.max_hale_class2: max_hale_classes[1],
                  ActiveRegion.max_hale_class3: max_hale_classes[2]})
    
    try:
        session.commit()
    
    except ValueError:
        print('Active Region noaa numbers NOT updated.')
        logging.debug('Active Region noaa numbers NOT updated.')
    
    else:
        print('Active Region noaa numbers updated.')
        logging.info('Active Region noaa numbers updated.')
    
    ###########################################################################
    # Ending the execution.
    #######################
    # Closing database session.
    session.close()
    print('Session closed')
    logging.info('Session closed')
    
    analysis_end = datetime.datetime.now()
    
    # Final feedback.
    for ar in noaa_numbers:
        if ar is not None:
            print('Active region ' + str(meta['noaa_ar']) + ' analysis completed.')
            print('Total Execution time: ', str(analysis_end - analysis_start))
        
        logging.info('Total Execution time: ' + str(analysis_end - analysis_start))
    
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
    
    # Defining the path to move the config file to.
    path_to_move = path+'used/'
    
    # Searching for the config files paths.
    path = glob.glob(path+'*.ini')
    
    # Iterating for each congif file.
    for config in path:
        print(f'Initiating the analysis for the file located ar: {config}')
        prepare(config_path=config, os_=os_)
        # Moving the config file to the used section.
        # rsplit will separate what is after and before the last slash.
        shutil.move(config, path_to_move + config.rsplit('/',1)[-1])
    
    # Feedback.    
    print('Finished.')
    
    return

if __name__ == '__main__':
    '''
    test zone
    '''
    execute_configs('mac')
