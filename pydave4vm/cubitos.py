#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This algorithm should prepare the datacubes to be used on the calling for
dave4vm. It will be necessary to adapt the path where the fits are located.

I guess that this code can actually be used for general pourposes to create 
datacubes with SDO files.


@author: andrechicrala
"""
#importing the 3rd party modules
import sunpy
import sunpy.map


def test_import():
    
    return(print('cubitos.py imported.'))
    
def create_cube(path_Br, path_Bp, path_Bt):
    
    #Defining the paths for files
    cube_Br = sunpy.map.Map(path_Br, sequence = True)
    cube_Bp = sunpy.map.Map(path_Bp, sequence = True)
    cube_Bt = sunpy.map.Map(path_Bt, sequence = True)
    
    #Creating empty lists to receive the datacubes data and metadata
    data_cube_Br = []
    data_cube_Bp = []
    data_cube_Bt = []
    meta_cube_Br = []
    meta_cube_Bp = []
    meta_cube_Bt = []    
    
    for i in range(0,len(cube_Br)):
    
        #This line will assign to the variables only the actual data without the 
        #header information that's also contained into the cube.
        #The output of this is a numpy array.
        data_cube_Br.append(cube_Br[i].data)
        data_cube_Bp.append(cube_Bp[i].data)
        data_cube_Bt.append(cube_Bt[i].data)
        
        #The output of this line will be the metadata.
        meta_cube_Br.append(cube_Br[i].meta)
        meta_cube_Bp.append(cube_Bp[i].meta)
        meta_cube_Bt.append(cube_Bt[i].meta)

    
    return(data_cube_Br, data_cube_Bp, data_cube_Bt, 
           meta_cube_Br, meta_cube_Bp, meta_cube_Bt)

if __name__ == '__main__':
    
    path_Br = '/Users/andrechicrala/Downloads/test2/*.Br.fits'
    path_Bp = '/Users/andrechicrala/Downloads/test2/*.Bp.fits'
    path_Bt = '/Users/andrechicrala/Downloads/test2/*.Bt.fits'
    a,b,c,d,f,g = create_cube(path_Br, path_Bp, path_Bt)
    
    
    