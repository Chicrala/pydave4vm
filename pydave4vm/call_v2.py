# !/usr/bin/env python3
#  -*- coding: utf-8 -*-
"""
Enter as argument for 'path' the path where the magnetic field components 
Bp, Br, Bt .fits files are located.

The 'window_size' can also be defined. The default value is 20.

@author: andrechicrala
"""

# importing basic packages
import pandas as pd
import numpy as np
import os
from datetime import datetime
from glob import glob

# calling my set of packages
from pydave4vm import do_dave4vm
from pydave4vm.addons.poyntingflux import poyntingflux
from pydave4vm.addons import cubitos3


def prep(path=None, path_out=None, window_size=None):
    '''
    description
    '''
    
    # defaulting the window size
    if window_size == None:
        # defining the window size
        print('Window size value not specified. \n',
        'Using default the window size of 20px.')
        window_size = 20
    
    # checking if a path was given
    while path == None:
        path = str(input('Please specify the path where the .fits are located: '))
        
        # checking if the given path exists
        if os.path.exists(path) == False:
            # if not, keep the value of path as none.
            print('The given path does not exists.')
            path = None
            
    # checking if a path was given
    while path_out == None:
        path_out = str(input('Please specify the path where the .fits are located: '))
        
        # checking if the given path exists
        if os.path.exists(path_out) == False:
            # if not, keep the value of path as none.
            print('The given path does not exists.')
            path_out = None
    
    # A dictionary to save the integrated values.
    int_values = {}
    
    for i in range(len(glob(path+'*.Bp.fits'))-1):
        # Feedback.
        print(f'Progress: {i}/'+str(len(glob(path+'*.Bp.fits'))-1))
        
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
        
        # defining a dx and dy in km based on HMI resolution
        dx = (2*np.pi*6.955e8*meta_cube_Bp[0]['CDELT2']/360)/1000
        dy = dx
        
        # Defining a dt in seconds
        t1 = datetime.strptime(meta_cube_Bp[0]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
        t2 = datetime.strptime(meta_cube_Bp[1]['t_obs'], "%Y.%m.%d_%H:%M:%S_TAI")
        dt = (t2-t1).total_seconds()
        
        # Calling do_dave4vm_and 
        magvm, vel4vm = do_dave4vm.do_dave4vm(dt,bx_stop,bx_start,by_stop,
                                                  by_start,bz_stop,bz_start,dx,
                                                  dy, window_size)
        
        # Checking if dave4vm was able to produce results.
        if vel4vm['solved'] is True:
        
            # calculating the Poynting flux        
            En, Et, Es, int_En, int_Et, int_Es = poyntingflux(dx,
                                                              magvm['bx'],
                                                              magvm['by'],
                                                              magvm['bz'],
                                                              vel4vm['U0'],
                                                              vel4vm['V0'],
                                                              vel4vm['W0'])
            
            
            # Exporting. Check if your folder is properly organized with
            # the correct subfolders.
            np.savetxt(path_out+'En/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', En, delimiter=',')
            np.savetxt(path_out+'Et/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', Et, delimiter=',')
            np.savetxt(path_out+'Bx/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', magvm['bx'], delimiter=',')
            np.savetxt(path_out+'By/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', magvm['by'], delimiter=',')
            np.savetxt(path_out+'Bz/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', magvm['bz'], delimiter=',')
            np.savetxt(path_out+'Vx/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', vel4vm['U0'], delimiter=',')
            np.savetxt(path_out+'Vy/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', vel4vm['V0'], delimiter=',')
            np.savetxt(path_out+'Vz/'+t2.strftime('%Y%m%d%H%M%S')+'.txt', vel4vm['W0'], delimiter=',')
            
            # Updating the dictionary.
            int_values[t2.strftime('%Y%m%d%H%M%S')] = {'int_En': int_En, 'int_Et': int_Et, 'int_Es': int_Es}
            
            # Releasing space.
            del magvm, vel4vm, En, Et, Es, int_En, int_Et, int_Es
            
        else:
            print('The apperture problem was NOT solved.')
            
    # Exporting the dataframe.
    df = pd.DataFrame(int_values).T
    df.to_csv(path_out+'bitmaped.csv', sep=',')
    
    return


if __name__ == "__main__":
    '''
    The testing zone
    '''
    
    # calling the function
    prep(path='/Volumes/chicrala/Data/6063/',path_out='/Volumes/chicrala/Bitmap/')  