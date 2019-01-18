#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This algorithm should prepare the datacubes to be used on the calling for
dave4vm. It will be necessary to adapt the path where the fits are located.

I guess that this code can actually be used for general pourposes to create 
datacubes with SDO files.

v2:
There is a minor difference in the number of results that will be returned.
Since only one meta data is needed, only one will be returned. Also,
this version receives only the main path and work out the others

V3:
This version is a little more optmized to do only pairs of fits per time.
The counter from the for loop is imported to keep track of the changes


@author: andrechicrala
"""
#importing the 3rd party modules
import sunpy
import sunpy.map
import glob
    
def create_cube(path, i):
    '''
    This module uses sunpy.map objects to 
    create datacubes with the information
    stored on the fits files.
    These cubes will be returned so that
    the data analisys can begin in other
    modules.
    '''
    #adapting the paths
    path_Br = [sorted(glob.glob(path+'*.Br.fits'))[i],
               sorted(glob.glob(path+'*.Br.fits'))[i+1]]
    
    path_Bp = [sorted(glob.glob(path+'*.Bp.fits'))[i],
               sorted(glob.glob(path+'*.Bp.fits'))[i+1]]
    
    path_Bt = [sorted(glob.glob(path+'*.Bt.fits'))[i],
               sorted(glob.glob(path+'*.Bt.fits'))[i+1]]
    
    #Defining the paths for files
    cube_Br = sunpy.map.Map(path_Br, sequence=True)
    cube_Bp = sunpy.map.Map(path_Bp, sequence=True)
    cube_Bt = sunpy.map.Map(path_Bt, sequence=True)
    
    #Creating empty lists to receive the datacubes data and metadata
    data_cube_Br = []
    data_cube_Bp = []
    data_cube_Bt = []
    meta_cube_Bp = []  
    
    for i in range(len(cube_Br)):
    
        #This line will assign to the variables only the actual data without the 
        #header information that's also contained into the cube.
        #The output of this is a numpy array.
        data_cube_Br.append(cube_Br[i].data)
        data_cube_Bp.append(cube_Bp[i].data)
        data_cube_Bt.append(cube_Bt[i].data)
        
        #The output of this line will be the metadata.
        meta_cube_Bp.append(cube_Bp[i].meta)

    
    return(data_cube_Br, data_cube_Bp, data_cube_Bt, 
           meta_cube_Bp)

if __name__ == '__main__':
    '''
    The classical testing zone
    '''
    
    i = 852
    path = '/Users/andrechicrala/Downloads/2587/'
    
    data_cube_Br, data_cube_Bp, data_cube_Bt, meta_cube_Bp = create_cube(path,i)
           