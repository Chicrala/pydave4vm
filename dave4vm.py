#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This algorithm is the one responsible for actually doing the calculation.
It uses another module to compute the huge matrix for the sake of practicity 
and to keep it more like the way it was initially designed in the original
dave4vm. 

Useful links with alternative methods to reform and convolve:
    http://mathesaurus.sourceforge.net/idl-numpy.html

@author: andrechicrala
"""
import numpy as np
import csv

from pydave4vm import dave4vm_matrix
from pydave4vm import matrix_test

#testing if the package was imported.
def dave4vmpy_test_import():
    
    return(print('dave4vm.py imported.'))  

#Calculating the trace of a 100 x imgY x imgX size matrix
def my_tracer(AM):
    
    trc = np.zeros((471,949))
    
    for i in range(0,8):
        trc = trc + AM[(i*10)+i] 
    
    
    return(trc)
    
#Function to create a base array of zeros
#Maybe empty like would be more appropriated to be used.
#'Criar' translates from create. 
def criar_array(dims):
    
    base_array = np.zeros((dims[0],dims[1]))
    
    return(base_array)


#the actual thing
def calculate_dave4vm(magvm,wsize):
    
    #Copying the dictionary to a variable    
    mag_dic = magvm
    
    #Defining arrays
    #Taking the shape of bz to later create arrays with the same shape.
    sz = mag_dic['bz'].shape
    
    
    #Constructing the weighting functions.
    nw = int(2*int(wsize/2)+1)
    
    #
    #
    ######the part below will have to be automated for the windowsize#########
    #
    #
    
    
    #Creating a numpy array based on the windowsize
    nw2 = np.subtract(np.array(range(0,nw)),10)
    
    #Creating the weighting functions
    x = np.array([nw2,]*nw)*mag_dic['dx']
    y = np.matrix.transpose(np.array([nw2,]*nw))*mag_dic['dy']    
    
    #Creating another array
    #Use double or float? initially I went with double
    psf = np.full((nw,nw), 1, dtype = 'double')
    
    #Normalizing this array
    psf = np.divide(psf, np.sum(psf))
    
    #Making futher operations
    psfx = np.multiply(psf,x)
    psfy = np.multiply(psf,y)
    psfxx = np.multiply(psf,np.multiply(x,x))
    psfyy = np.multiply(psf,np.multiply(y,y))
    psfxy = np.multiply(np.multiply(psf,x),y)
    
    
    #Keeping those guys in a dictionary.
   # kernel = {'psf': psf, 'psfx': psfx, 'psfy': psfy, 'psfxx': psfxx,
    #          'psfyy': psfyy, 'psfxy': psfxy}
    
    
    #Calling the next function!
    #the_matrix(bx, bxx, bxy, by, byx, byy, bz, bzx, bzy,
    #           bzt, psf, psfx, psfy, psfxx, psfyy, psfxy):
    AM = dave4vm_matrix.the_matrix(mag_dic['bx'], mag_dic['bxx'], 
                                   mag_dic['bxy'], mag_dic['by'], 
                                   mag_dic['byx'], mag_dic['byy'],
                                   mag_dic['bz'], mag_dic['bzx'],
                                   mag_dic['bzy'], mag_dic['bzt'],
                                   psf, psfx, psfy, psfxx, psfyy, psfxy)
    
    
    #Estimating the trace
    #This line will sum each 'lay' of the AM matrix
    trc = my_tracer(AM)
    #Indexing the points where the trace is greater than a given threshold
    index = np.where(trc > 1000)
    
    #Reshaping, this will make it easier to separate the values for the least
    #squares function to calculate.
    AM = np.reshape(AM,(10,10,471,949))
    
    #creating lists to receive the data
    U0 = criar_array(sz)
    V0 = criar_array(sz)
    UX = criar_array(sz)
    VY = criar_array(sz)
    UY = criar_array(sz)
    VX = criar_array(sz)
    W0 = criar_array(sz)
    WX = criar_array(sz)
    WY = criar_array(sz)
    
    
    #Building the for loop to go over the "good" pixels
    for i in range(0,len(index[0])):
        '''
        #Calculating the j,i coordinates
        j = index[i]//sz[1] #take the integer part of this division
        i = index[i]%sz[1] #take the remainder of this division
        '''
        #Calculating the j,i coordinates
        #This is a bit different. CONFERIR DEPOIS!!!!!!!
        y = index[0][i]
        x = index[1][i]

        #Taking a chunk of the matrix AM
        #In relation to the original dave4vm code in IDL the
        AA = AM[:,:,y,x]
        
        #Taking among all the itens defined by the i,j coordinates
        #the first nine itens as a matrix
        GA = AA[0:9,0:9]
        
        #Now building a column matrix with the last elements, the remaining
        #itens of AA. Those itens are multiplied by -1 and reshaped to be used
        #in the linear regression
        FA = -1*np.reshape(AA[0:9,9],9)

        #performing the linear regression between the data held by the 
        #variables GA and FA.
        #The results that will actually compose the plasma velocities are
        #held on the first item of the tuple.
        #This method also uses the divide and conquer algorithm
        #http://drsfenner.org/blog/2015/12/three-paths-to-least-squares-linear-regression/
        vector = np.linalg.lstsq(GA, FA)
        
        #Assigning the results to the respective variables
        U0[y,x] = vector[0][0]
        V0[y,x] = vector[0][1]
        UX[y,x] = vector[0][2]
        VY[y,x] = vector[0][3]
        UY[y,x] = vector[0][4]
        VX[y,x] = vector[0][5]
        W0[y,x] = vector[0][6]
        WX[y,x] = vector[0][7]
        WY[y,x] = vector[0][8]
        
        
    #Creating a dictionary to hold the final results
    #v = {'U0': }  
    vel4vm = np.stack((U0,V0,UX,VY,UY,VX,W0,WX,WY), axis = 0)
    
    return(vel4vm,trc)
    
    

