#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This algorithm is the one responsible for actually doing the calculation.
It uses another module to compute the huge matrix for the sake of practicity 
and to keep it more like the way it was initially designed in the original
dave4vm. 

@author: andrechicrala
"""
import numpy as np
from pydave4vm import dave4vm_matrix
from numpy.linalg import solve
import copy


#the actual thing
def calculate_dave4vm(magvm,wsize):
    '''
    This is the main body of DAVE4VM. Here the kernel is built,
    the convolutions performed and the system solutions are calculated
    returning the dictionary with the values.
    '''
    
    #Copying the dictionary to a variable    
    mag_dic = copy.copy(magvm)
    
    #Defining arrays
    #Taking the shape of bz to later create arrays with the same shape.
    sz = mag_dic['bz'].shape
    
    #creating lists to receive the data
    #creating "dummy" variables
    U0 = np.zeros((sz[0],sz[1]))
    V0 = np.zeros((sz[0],sz[1]))
    UX = np.zeros((sz[0],sz[1]))
    VY = np.zeros((sz[0],sz[1]))
    UY = np.zeros((sz[0],sz[1]))
    VX = np.zeros((sz[0],sz[1]))
    W0 = np.zeros((sz[0],sz[1]))
    WX = np.zeros((sz[0],sz[1]))
    WY = np.zeros((sz[0],sz[1]))
        
    #Constructing the weighting functions.
    nw = int(2*int(wsize/2)+1)
        
    #Creating a numpy array based on the windowsize
    nw2 = np.subtract(np.array(range(0,nw)),10) #check if nw should have an index associated to it
        
    #Creating the weighting functions
    x = np.array([nw2,]*nw)*mag_dic['dx']
    y = np.matrix.transpose(np.array([nw2,]*nw))*mag_dic['dy']
        
    #Creating another array
    #Use double or float? initially I went with double
    psf = np.full((nw,nw), 1, dtype = 'float64')
    
    #Normalizing this array
    psf = np.divide(psf, np.sum(psf)) 
    
    #Making futher operations
    psfx = -np.multiply(psf,x)
    psfy = -np.multiply(psf,y)
    psfxx = np.multiply(psf,np.multiply(x,x))
    psfyy = np.multiply(psf,np.multiply(y,y))
    psfxy = np.multiply(np.multiply(psf,x),y)
    
    #defining the kernel as a dictionary
    kernel = {'psf': psf, 'psfx': psfx, 
              'psfy': psfy, 'psfxx': psfxx,
              'psfyy': psfyy, 'psfxy': psfxy}
    
    #Calling the next function!
    AM = dave4vm_matrix.the_matrix(mag_dic['bx'], mag_dic['bxx'], 
                                   mag_dic['bxy'], mag_dic['by'], 
                                   mag_dic['byx'], mag_dic['byy'],
                                   mag_dic['bz'], mag_dic['bzx'],
                                   mag_dic['bzy'], mag_dic['bzt'],
                                   kernel['psf'], kernel['psfx'], 
                                   kernel['psfy'], kernel['psfxx'], 
                                   kernel['psfyy'], kernel['psfxy'])
    
    #reshaping the matrix
    AM = np.reshape(AM,(10,10,sz[0],sz[1]))

    #computing the trace with numpy
    trc = np.trace(AM, axis1 = 0, axis2 = 1)
    
    #indexing points where the trace is bigger than 1
    index = np.where(trc > 1)
    
    #for i in range(0,len(index[0])):    
    for i,j in zip(index[0],index[1]):
        #taking a chunk of AM at the specified point
        #AA = AM[:,:,index[0][i],index[1][i]]
        AA = AM[:,:,i,j]
        
        #taking the first 9 columns to build ''ax''
        GA = AA[0:9,0:9]
        
        #taking the last column to build ''b''
        FA = -1*np.reshape(AA[9,0:9],9)
        
        #defining a vector to receive the answers
        vector = solve(GA,FA)
        #assigning the values to the matrices
        U0[i,j] = vector[0]
        V0[i,j] = vector[1]
        UX[i,j] = vector[2]
        VY[i,j] = vector[3]
        UY[i,j] = vector[4]
        VX[i,j] = vector[5]
        W0[i,j] = vector[6]
        WX[i,j] = vector[7]
        WY[i,j] = vector[8]
        
    #Organizing the variables in a dictionary
    vel4vm = {'U0': U0, 'UX': UX, 'UY': UY,
              'V0': V0, 'VX': VX, 'VY': VY,
              'W0': W0, 'WX': WX, 'WY': WY}
    
    return(vel4vm)
    
    

