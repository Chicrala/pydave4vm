#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code represents my pre-call for pydave4vm algorithm.
Here data is setup to serve as an entry to the actual code that will call dave4vm
which is do_dave4vm_and.py

Enter as argument for 'path' the path where the magnetic field components 
Bp, Br, Bt .fits files are located.

The 'window_size' can also be defined. The default value is 20.

@author: andrechicrala
"""

#importing basic packages
import numpy as np
import os
from datetime import datetime

#calling my set of packages
from pydave4vm import cubitos
from pydave4vm import do_dave4vm_and


def call_v1(path = None, window_size = None):
    '''
    description
    '''
    
    #defaulting the window size
    if window_size == None:
        #defining the window size
        print('Window size value not specified. \n',
        'Using default the window size of 20px.')
        window_size = 20
    
    #checking if a path was given
    while path == None:
        path = str(input('Please specify the path where the .fits are located: '))
        
        #checking if the given path exists
        if os.path.exists(path) == False:
            #if not, keep the value of path as none.
            print('The given path does not exists.')
            path = None


    #Calling the cubitos.py function to make the datacubes.
    #Don't forget to adapt the paths if necessary!
    path_Br = path+'*.Br.fits'
    path_Bp = path+'*.Bp.fits'
    path_Bt = path+'*.Bt.fits'
    
    data_cube_Br, data_cube_Bp, data_cube_Bt, meta_cube_Br,\
    meta_cube_Bp, meta_cube_Bt = cubitos.create_cube(path_Br, path_Bp, path_Bt)
    
    #defining a dx and dy in km based on HMI resolution
    dx = (2*np.pi*6.955e8*meta_cube_Bp[0]['CDELT2']/360)/1000
    dy = dx
    
    #Defining the start and end points based on the datacubes.
    bx_start = data_cube_Bp[0]
    by_start = np.multiply(-1,data_cube_Bt[0])
    bz_start = data_cube_Br[0]
    bx_stop = data_cube_Bp[1]
    by_stop = np.multiply(-1,data_cube_Bt[1])
    bz_stop = data_cube_Br[1]
    
    #Defining a dt in seconds
    t1 = datetime.strptime(meta_cube_Bp[0]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
    t2 = datetime.strptime(meta_cube_Bp[1]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
    dt = (t2-t1).total_seconds()
    
    #Calling do_dave4vm_and 
    magvm, vel4vm = do_dave4vm_and.do_dave4vm(dt,bx_stop,bx_start,by_stop,
                                              by_start,bz_stop,bz_start,dx,
                                              dy, window_size)
    
    return(magvm, vel4vm)


if __name__ == "__main__":
    '''
    The testing zone
    '''
    
    #calling the function
    magvm, vel4vm = call_v1()  