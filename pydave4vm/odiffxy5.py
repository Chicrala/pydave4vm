#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 13:02:55 2017

link ref: http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
https://www.pythoncentral.io/introduction-to-sqlite-in-python/

@author: andrechicrala
"""

import numpy as np

def odiff(image):
    
    '''
    Image refers to the image of the magnetic field in x,y,z or, in this case, to
    the average of the initial and stop values of them.
    '''
    
    #defining the constants
    c1 = 0.12019
    c2 = 0.74038
    #The number format "d0" on idl doesn't seems to be relevant
    #for python.
    
    #Calculating the shifts
    #The "a's" will be used to calculate dx and the "b's" to calculate dy
    a1 = np.roll(image[:], -2, axis = 1) #two pxs to the left
    a2 = np.roll(image[:], -1, axis = 1) #one px to the left
    a3 = np.roll(image[:], 1, axis = 1) #one px to the right
    a4 = np.roll(image[:], 2, axis = 1) #two pxs to the right
    
    b1 = np.roll(image[:], -2, axis = 0) #two pxs downward
    b2 = np.roll(image[:], -1, axis = 0) #one px downward
    b3 = np.roll(image[:], 1, axis = 0) #one px upward
    b4 = np.roll(image[:], 2, axis = 0) #two pxs upward
    
    #Calculating the differentials dx and dy using the shift_pxs function results
    dx = (np.multiply(-c1,a1) + np.multiply(c2,a2) + np.multiply(-c2,a3) +
          np.multiply(c1,a4))
    dy =(np.multiply(-c1,b1) + np.multiply(c2,b2) + np.multiply(-c2,b3) +
          np.multiply(c1,b4))
    
    return(dx,dy)

