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


use con and get like here:
    https://gist.github.com/maedoc/b5b3cd91aaa59ec573f9
    
    

@author: andrechicrala
"""

#importing basic packages
import numpy as np
from datetime import datetime

#calling my set of packages
from pydave4vm import cubitos
from pydave4vm import do_dave4vm_and
from and_mods.poyntingflux import poyntingflux

#importing the packages to create the session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sql
#import json

#importing the classes
from and_db.dbtest import Base, ActiveRegion, Observations

#quick function to pass data to string
def ajuste(data):
    
    return(data.tostring())


def call_v3():
    '''
    description
    '''
    
    #defining the window size
    window_size = 20
    
    #Calling the cubitos.py function to make the datacubes.
    #Don't forget to adapt the paths if necessary!
    
    path_Br = '/Users/andrechicrala/Downloads/test/*.Br.fits'
    path_Bp = '/Users/andrechicrala/Downloads/test/*.Bp.fits'
    path_Bt = '/Users/andrechicrala/Downloads/test/*.Bt.fits'
    
    '''
    path_Br = '/Users/andrechicrala/Downloads/dbtest/*.Br.fits'
    path_Bp = '/Users/andrechicrala/Downloads/dbtest/*.Bp.fits'
    path_Bt = '/Users/andrechicrala/Downloads/dbtest/*.Bt.fits'
    '''
    
    data_cube_Br, data_cube_Bp, data_cube_Bt, meta_cube_Br,\
    meta_cube_Bp, meta_cube_Bt = cubitos.create_cube(path_Br, path_Bp, path_Bt)
    
    #defining a dx and dy in km based on HMI resolution
    #used 1000 before!
    dx = (2*np.pi*6.955e8*meta_cube_Bp[0]['CDELT2']/360)/1000
    dy = dx
    
    #creating the sql engine:
    engine = create_engine('sqlite:////Users/andrechicrala/anaconda3/lib/python3.6/site-packages/and_db/testdb.db')
    
    #declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    #binding the engine
    DBSession = sessionmaker(bind = engine)
    #creating a session object
    session = DBSession()
    
    #the first session should create an item for the active region
    #using its noaa and harp numbers
    #starting session
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
            print('AR not inserted into the database.')
    
    #checking the number
    s = sql.select([ActiveRegion]).where(
                ActiveRegion.harp_number == meta_cube_Bp[0]['harpnum'])
    #creating te result proxy
    rp = session.execute(s)
    #getting the results
    ar_id = rp.fetchall()[0]
    
    #prints to state progress
    print('NOAA', meta_cube_Bp[0]['noaa_ar'], 'commited to the system.')
    
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
        #session = DBSession()
        #new_obs = Observations(timestamp = t2)
        #session.add(new_obs)
        #session.commit()
        
        #prints to state progress
        print('Timestamp', meta_cube_Bp[i+1]['t_obs'], 'created.')
        
        #Calling do_dave4vm_and 
        magvm, vel4vm = do_dave4vm_and.do_dave4vm(dt,bx_stop, bx_start, by_stop,
                                                  by_start, bz_stop, bz_start,dx,
                                                  dy, window_size)
        
        columnshape = np.shape(vel4vm['U0'])[0]
        
        #calculating the Poynting flux        
        En, Et, Es, int_En, int_Et, int_Es = poyntingflux(dx,
                                                          magvm['bx'],
                                                          magvm['by'],
                                                          magvm['bz'],
                                                          vel4vm['U0'],
                                                          vel4vm['V0'],
                                                          vel4vm['W0'])
        
        
        #here the actual data is led into the database
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

        #prints to state progress
        print('Data add.')
        
            
        #feedback
        print(meta_cube_Bp[i]['t_obs'], ' Processed! =D')
    
    return(magvm,vel4vm, En, Et, Es, int_En, int_Et, int_Es)


if __name__ == "__main__":
    '''
    The testing zone
    '''
    magvm,vel4vm, En, Et, Es, int_En, int_Et, int_Es = call_v3()
    

    
        
        
