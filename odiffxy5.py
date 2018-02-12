#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 13:02:55 2017

link ref: http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
https://www.pythoncentral.io/introduction-to-sqlite-in-python/

@author: andrechicrala
"""
from pydave4vm import cubitos
from pydave4vm import and_plot as ap
import numpy as np

def test_import():
    
    return(print('odiffxy5.py imported.'))

#This function should shift the position of rows and columns of pixels
#For the sake of completness, eixo means axis in portuguese.
#Eixo must be an integer being 0 for y-axis and 1 for x-axis
def shift_pxs(data,npx,eixo):
    
    #Rolling the elements
    shifted_data = np.roll(data, npx,axis = eixo)
    
    return(shifted_data)
    

#Image refers to the image of the magnetic field in x,y,z or, in this case, to
#the average of the initial and stop values of them.
def odiff(image):
    
    #defining the constants
    c1 = 0.12019
    c2 = 0.74038
    #The number format "d0" on idl doesn't seems to be relevant
    #for python.
    
    #Calculating the shifts
    #The "a's" will be used to calculate dx and the "b's" to calculate dy
    a1 = shift_pxs(image,-2,1) #two pxs to the left
    a2 = shift_pxs(image,-1,1) #one px to the left
    a3 = shift_pxs(image,1,1) #one px to the right
    a4 = shift_pxs(image,2,1) #two pxs to the right
    
    b1 = shift_pxs(image,-2,0) #two pxs downward
    b2 = shift_pxs(image,-1,0) #one px downward
    b3 = shift_pxs(image,1,0) #one px upward
    b4 = shift_pxs(image,2,0) #two pxs upward
    
    
    
    #Calculating the differentials dx and dy using the shift_pxs function results
    dx = (np.multiply(-c1,a1) + np.multiply(c2,a2) + np.multiply(-c2,a3) +
          np.multiply(c1,a4))
    dy =(np.multiply(-c1,b1) + np.multiply(c2,b2) + np.multiply(-c2,b3) +
          np.multiply(c1,b4))
    
    
    return(dx,dy)


'''
######
######For testing pourposes only
######
#Calling the cubitos.py function to make the datacubes.
#Don't forget to adapt the paths if necessary!
path_Br = '/Users/andrechicrala/Downloads/fits/*.Br.fits'
path_Bp = '/Users/andrechicrala/Downloads/fits/*.Bp.fits'
path_Bt = '/Users/andrechicrala/Downloads/fits/*.Bt.fits'

data_cube_Br, data_cube_Bp, data_cube_Bt, meta_cube_Br, meta_cube_Bp, meta_cube_Bt = cubitos.create_cube(path_Br, path_Bp, path_Bt)

#Defining the start and end points based on the datacubes.
#This should later be included in a for structure depending on the objective.
bx_start = data_cube_Bp[0]
by_start = np.multiply(-1,data_cube_Bt[0]) #need to multiply this for -1 at some point later on
bz_start = data_cube_Br[0]
bx_stop = data_cube_Bp[1]
by_stop = np.multiply(-1,data_cube_Bt[1]) #need to multiply this for -1 at some point later on
bz_stop = data_cube_Br[1]

ap.simples_plot(bx_start)

a = shift_pxs(bx_start,-200,1)
ap.simples_plot(a)

b = odiff(bx_start)
print(b,len(b))

ap.simples_plot(b)
'''



