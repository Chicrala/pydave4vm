#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 13:02:55 2017

link ref: http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
https://www.pythoncentral.io/introduction-to-sqlite-in-python/

@author: andrechicrala
"""

###importing packages###

import numpy as np
from astropy.convolution import convolve#, convolve_fft


#The massive matrix described on dr. Chuck paper (2008)
def the_matrix(bx, bxx, bxy, by, byx, byy, bz, bzx, bzy,
               bzt, psf, psfx, psfy, psfxx, psfyy, psfxy):
    
    #Remember that shape returns as y,x 
    #Taking the shape of bz
    #sz = bz.shape
    
    #Constructing the matrix for the LKA algorithm
    #Later I should take those unecessary terms to hold the multiplication away
    #G = np.convolve(np.multiply(bz,bz),psf, normalize_kernel=False)
    GG = np.multiply(bz,bz)
    G = convolve(GG,psf, normalize_kernel=False) #1
    
    '''
    print('The convolution is: ', G)
    print('The shape is: ', G.shape)
    print('The maximum value is: ', np.amax(G))
    print('The minimum value is: ', np.amin(G))
    
    
    G2 = convolve_fft(GG,psf)
    
    print('The convolution is: ', G2)
    print('The shape is: ', G2.shape)
    print('The maximum value is: ', np.amax(G2))
    print('The minimum value is: ', np.amin(G2))
    
    G3 = np.subtract(G,G2)
    
    print('The convolution is: ', G3)
    print('The shape is: ', G3.shape)
    print('The maximum value is: ', np.amax(G3))
    print('The minimum value is: ', np.amin(G3))
    
    ##########################
    
    '''
    
    GGx = np.multiply(bz,bzx)
    Gx = convolve(GGx,psf, normalize_kernel=False) #2
    
    xGx = convolve(GGx,psfx, normalize_kernel=False) #3 Yey!
    
    yGx = convolve(GGx,psfy, normalize_kernel=False) #4
    
    GGy = np.multiply(bz,bzy)
    Gy = convolve(GGy,psf, normalize_kernel=False) #5
    
    xGy = convolve(GGy,psfx, normalize_kernel=False) #6
    
    yGy = convolve(GGy,psfy, normalize_kernel=False) #7
    
    GGt = np.multiply(bzt,bz)
    Ht = convolve(GGt,psf, normalize_kernel=False) #8
    
    GGxx = np.multiply(bzx,bzx)
    Gxx = convolve(GGxx,psf, normalize_kernel=False) #9
    
    GGyy = np.multiply(bzy,bzy)
    Gyy = convolve(GGyy,psf, normalize_kernel=False) #10
    
    GGxy = np.multiply(bzx,bzy)
    Gxy = convolve(GGxy,psf, normalize_kernel=False) #11
    
    GGtx = np.multiply(bzt,bzx)
    Gtx = convolve(GGtx,psf, normalize_kernel=False) #12
    
    GGty = np.multiply(bzt,bzy) 
    Gty = convolve(GGty, psf, normalize_kernel=False) #13
    ##########################
    
    ##########################
    xGxx = convolve(GGxx,psfx, normalize_kernel=False) #14
    xGyy = convolve(GGyy,psfx, normalize_kernel=False) #15
    xGxy = convolve(GGxy,psfx, normalize_kernel=False) #16
    xGtx = convolve(GGtx,psfx, normalize_kernel=False) #17
    xGty = convolve(GGty,psfx, normalize_kernel=False) #18
    ##########################
    
    ##########################
    yGxx = convolve(GGxx,psfy, normalize_kernel=False) #19
    yGyy = convolve(GGyy,psfy, normalize_kernel=False) #20
    yGxy = convolve(GGxy,psfy, normalize_kernel=False) #21
    yGtx = convolve(GGtx,psfy, normalize_kernel=False) #22
    yGty = convolve(GGty,psfy, normalize_kernel=False) #23
    ##########################
    
    ##########################
    xxGxx = convolve(GGxx,psfxx, normalize_kernel=False) #24
    xxGxy = convolve(GGxy,psfxx, normalize_kernel=False) #25
    xxGyy = convolve(GGyy,psfxx, normalize_kernel=False) #26  
    ##########################
    
    ##########################
    xyGxx = convolve(GGxx,psfxy, normalize_kernel=False) #27
    xyGxy = convolve(GGxy,psfxy, normalize_kernel=False) #28
    xyGyy = convolve(GGyy,psfxy, normalize_kernel=False) #29  
    ##########################
    
    ##########################
    yyGxx = convolve(GGxx,psfyy, normalize_kernel=False) #30
    yyGxy = convolve(GGxy,psfyy, normalize_kernel=False) #31
    yyGyy = convolve(GGyy,psfyy, normalize_kernel=False) #32  
    ##########################
    
    GGtt = np.multiply(bzt,bzt)
    Gtt = convolve(GGtt,psf)  #33
    
    ##########################
    #End of the original dave matrices
    ##########################
    #For now on there are represented the extra vector magnetogram terms
    
    BxBx = convolve(np.multiply(bx,bx),psf, normalize_kernel=False)
    ByBy = convolve(np.multiply(by,by),psf, normalize_kernel=False)
    BxBy = convolve(np.multiply(bx,by),psf, normalize_kernel=False)
    BzBx = convolve(np.multiply(bz,bx),psf, normalize_kernel=False)
    BzBy = convolve(np.multiply(bz,by),psf, normalize_kernel=False)
    
    BxBxx = convolve(np.multiply(bx,bxx),psf, normalize_kernel=False)
    BxByy = convolve(np.multiply(bx,byy),psf, normalize_kernel=False)
    BxxBxx = convolve(np.multiply(bxx,bxx),psf, normalize_kernel=False)
    ByyByy = convolve(np.multiply(byy,byy),psf, normalize_kernel=False)
    BxxByy = convolve(np.multiply(bxx,byy),psf, normalize_kernel=False)
    ByBxx = convolve(np.multiply(by,bxx),psf, normalize_kernel=False)
    ByByy = convolve(np.multiply(by,byy),psf, normalize_kernel=False)
    
    BzBxx = convolve(np.multiply(bz,bxx),psf, normalize_kernel=False)
    BzByy = convolve(np.multiply(bz,byy),psf, normalize_kernel=False)
    
    BztBxx = convolve(np.multiply(bzt,bxx),psf, normalize_kernel=False)
    BztByy = convolve(np.multiply(bzt,byy),psf, normalize_kernel=False)
    
    BzxBx = convolve(np.multiply(bzx,bx),psf, normalize_kernel=False)
    BzxBy = convolve(np.multiply(bzx,by),psf, normalize_kernel=False)
    BzxBxx = convolve(np.multiply(bzx,bxx),psf, normalize_kernel=False)
    BzxByy = convolve(np.multiply(bzx,byy),psf, normalize_kernel=False)
    
    BzyBx = convolve(np.multiply(bzy,bx),psf, normalize_kernel=False)
    BzyBy = convolve(np.multiply(bzy,by),psf, normalize_kernel=False)
    BzyBxx = convolve(np.multiply(bzy,bxx),psf, normalize_kernel=False)
    BzyByy = convolve(np.multiply(bzy,byy),psf, normalize_kernel=False)
    
    BztBx = convolve(np.multiply(bzt,bx),psf, normalize_kernel=False)
    BztBy = convolve(np.multiply(bzt,by),psf, normalize_kernel=False)
    
    ##########################
    #End of the psf dependent convolutions
    ##########################
    
    
    xBzxBx = convolve(np.multiply(bzx,bx),psfx, normalize_kernel=False)
    xBzxBy = convolve(np.multiply(bzx,by),psfx, normalize_kernel=False)
    xBzyBx = convolve(np.multiply(bzy,bx),psfx, normalize_kernel=False)
    xBzyBy = convolve(np.multiply(bzy,by),psfx, normalize_kernel=False)
    
    yBzyBx = convolve(np.multiply(bzy,bx),psfy, normalize_kernel=False)
    yBzyBy = convolve(np.multiply(bzy,by),psfy, normalize_kernel=False)
    
    yBzxBx = convolve(np.multiply(bzx,bx),psfy, normalize_kernel=False)
    yBzxBy = convolve(np.multiply(bzx,by),psfy, normalize_kernel=False)
    
    yBxBxx = convolve(np.multiply(bx,bxx),psfy, normalize_kernel=False)
    yBxByy = convolve(np.multiply(bx,byy),psfy, normalize_kernel=False)
    
    yByBxx = convolve(np.multiply(by,bxx),psfy, normalize_kernel=False)
    yByByy = convolve(np.multiply(by,byy),psfy, normalize_kernel=False)
    
    xByBxx = convolve(np.multiply(by,bxx),psfx, normalize_kernel=False)
    xByByy = convolve(np.multiply(by,byy),psfx, normalize_kernel=False)
    
    xBzxBxx = convolve(np.multiply(bzx,bxx),psfx, normalize_kernel=False)
    xBzxByy = convolve(np.multiply(bzx,byy),psfx, normalize_kernel=False)
    
    yBzxBxx = convolve(np.multiply(bzx,bxx),psfy, normalize_kernel=False)
    yBzxByy = convolve(np.multiply(bzx,byy),psfy, normalize_kernel=False)
    
    xBxxBxx = convolve(np.multiply(bxx,bxx),psfx, normalize_kernel=False)
    xBxxByy = convolve(np.multiply(bxx,byy),psfx, normalize_kernel=False)
    xByyByy = convolve(np.multiply(byy,byy),psfx, normalize_kernel=False)
    
    yBxxBxx = convolve(np.multiply(bxx,bxx),psfy, normalize_kernel=False) 
    yBxxByy = convolve(np.multiply(bxx,byy),psfy, normalize_kernel=False)
    yByyByy = convolve(np.multiply(byy,byy),psfy, normalize_kernel=False)
    
    xBxBxx = convolve(np.multiply(bx,bxx),psfx, normalize_kernel=False)
    xBxByy = convolve(np.multiply(bx,byy),psfx, normalize_kernel=False)
    
    xBzBxx = convolve(np.multiply(bz,bxx),psfx, normalize_kernel=False)
    xBzByy = convolve(np.multiply(bz,byy),psfx, normalize_kernel=False)
    
    xBztBxx = convolve(np.multiply(bzt,bxx),psfx, normalize_kernel=False)
    xBztByy = convolve(np.multiply(bzt,byy),psfx, normalize_kernel=False)
    
    yBztBxx = convolve(np.multiply(bzt,bxx),psfy, normalize_kernel=False)
    yBztByy = convolve(np.multiply(bzt,byy),psfy, normalize_kernel=False)
    
    xyBxxBxx = convolve(np.multiply(bxx,bxx),psfxy, normalize_kernel=False)
    xyBxxByy = convolve(np.multiply(bxx,byy),psfxy, normalize_kernel=False)
    xyByyByy = convolve(np.multiply(byy,byy),psfxy, normalize_kernel=False)
    
    xyBzxBxx = convolve(np.multiply(bzx,bxx),psfxy, normalize_kernel=False)
    xyBzxByy = convolve(np.multiply(bzx,byy),psfxy, normalize_kernel=False)
    xyBzyBxx = convolve(np.multiply(bzy,byy),psfxy, normalize_kernel=False)
    xyBzyByy = convolve(np.multiply(bzy,byy),psfxy, normalize_kernel=False)
    
    yBzBxx = convolve(np.multiply(bz,bxx),psfy, normalize_kernel=False)
    yBzByy = convolve(np.multiply(bz,byy),psfy, normalize_kernel=False)
    
    xBzyBxx = convolve(np.multiply(bzy,bxx),psfx, normalize_kernel=False)
    xBzyByy = convolve(np.multiply(bzy,byy),psfx, normalize_kernel=False)
    yBzyBxx = convolve(np.multiply(bzy,byy),psfy, normalize_kernel=False)
    yBzyByy = convolve(np.multiply(bzy,byy),psfy, normalize_kernel=False)
    
    xxBxxBxx = convolve(np.multiply(bxx,bxx),psfxx, normalize_kernel=False)
    xxBxxByy = convolve(np.multiply(bxx,byy),psfxx, normalize_kernel=False)
    xxByyByy = convolve(np.multiply(byy,byy),psfxx, normalize_kernel=False)
    
    xxBzxBxx = convolve(np.multiply(bzx,bxx),psfxx, normalize_kernel=False)
    xxBzyBxx = convolve(np.multiply(bzy,bxx),psfxx, normalize_kernel=False)
    xxBzxByy = convolve(np.multiply(bzx,byy),psfxx, normalize_kernel=False)
    xxBzyByy = convolve(np.multiply(bzy,byy),psfxx, normalize_kernel=False)
    
    yyBxxBxx = convolve(np.multiply(bxx,bxx),psfyy, normalize_kernel=False)
    yyBxxByy = convolve(np.multiply(bxx,byy),psfyy, normalize_kernel=False)
    yyByyByy = convolve(np.multiply(byy,byy),psfyy, normalize_kernel=False)
    
    yyBzyBxx = convolve(np.multiply(bzy,bxx),psfyy, normalize_kernel=False)
    yyBzyByy = convolve(np.multiply(bzy,byy),psfyy, normalize_kernel=False)
    
    yyBzxBxx = convolve(np.multiply(bzx,bxx),psfyy, normalize_kernel=False)
    yyBzxByy = convolve(np.multiply(bzx,byy),psfyy, normalize_kernel=False)
    
    #############End of individual terms calculation##################
    
    ###
    ### Remake this bit using numpy and properly indexing.
    ###

    
    A = np.stack((Gxx, Gxy, Gx + xGxx, Gx + yGxy, yGxx, xGxy, -BzxBxx - BzxByy, 
  -BzxBx - xBzxBxx - xBzxByy, -BzxBy - yBzxBxx - yBzxByy, Gtx,
 Gxy, Gyy, Gy + xGxy, Gy + yGyy, yGxy, xGyy, -BzyBxx - BzyByy,
  -BzyBx - xBzyBxx - xBzyByy, -BzyBy - yBzyBxx - yBzyByy, Gty, 
 Gx + xGxx, Gy + xGxy, G + 2*xGx + xxGxx, G + xGx + xyGxy + yGy, 
  xyGxx + yGx, xGy + xxGxy, -BzBxx - BzByy - xBzxBxx - xBzxByy, 
  -BzBx - xBzBxx - xBzByy - xBzxBx - xxBzxBxx - xxBzxByy, 
  -BzBy - xBzxBy - xyBzxBxx - xyBzxByy - yBzBxx - yBzByy, Ht + xGtx, 
 Gx + yGxy, Gy + yGyy, G + xGx + xyGxy + yGy, G + 2*yGy + yyGyy, 
  yGx + yyGxy, xGy + xyGyy, -BzBxx - BzByy - yBzyBxx - yBzyByy, 
  -BzBx - xBzBxx - xBzByy - xyBzyBxx - xyBzyByy - yBzyBx, 
  -BzBy - yBzBxx - yBzByy - yBzyBy - yyBzyBxx - yyBzyByy, Ht + yGty, 
 yGxx, yGxy, xyGxx + yGx, yGx + yyGxy, yyGxx, xyGxy, -yBzxBxx - yBzxByy, 
  -xyBzxBxx - xyBzxByy - yBzxBx, -yBzxBy - yyBzxBxx - yyBzxByy, yGtx, 
 xGxy, xGyy, xGy + xxGxy, xGy + xyGyy, xyGxy, xxGyy, -xBzyBxx - xBzyByy, 
  -xBzyBx - xxBzyBxx - xxBzyByy, -xBzyBy - xyBzyBxx - xyBzyByy, xGty, 
 -BzxBxx - BzxByy, -BzyBxx - BzyByy, -BzBxx - BzByy - xBzxBxx - xBzxByy, 
  -BzBxx - BzByy - yBzyBxx - yBzyByy, -yBzxBxx - yBzxByy, -xBzyBxx - xBzyByy, 
  BxxBxx + 2*BxxByy + ByyByy, BxBxx + BxByy + xBxxBxx + 2*xBxxByy + xByyByy, 
  ByBxx + ByByy + yBxxBxx + 2*yBxxByy + yByyByy, -BztBxx - BztByy, 
 -BzxBx - xBzxBxx - xBzxByy, -BzyBx - xBzyBxx - xBzyByy, 
  -BzBx - xBzBxx - xBzByy - xBzxBx - xxBzxBxx - xxBzxByy, 
  -BzBx - xBzBxx - xBzByy - xyBzyBxx - xyBzyByy - yBzyBx, 
  -xyBzxBxx - xyBzxByy - yBzxBx, -xBzyBx - xxBzyBxx - xxBzyByy, 
  BxBxx + BxByy + xBxxBxx + 2*xBxxByy + xByyByy, 
  BxBx + 2*xBxBxx + 2*xBxByy + xxBxxBxx + 2*xxBxxByy + xxByyByy, 
  BxBy + xByBxx + xByByy + xyBxxBxx + 2*xyBxxByy + xyByyByy + yBxBxx + 
   yBxByy, -BztBx - xBztBxx - xBztByy, -BzxBy - yBzxBxx - yBzxByy, 
  -BzyBy - yBzyBxx - yBzyByy, -BzBy - xBzxBy - xyBzxBxx - xyBzxByy - yBzBxx - 
   yBzByy, -BzBy - yBzBxx - yBzByy - yBzyBy - yyBzyBxx - yyBzyByy, 
  -yBzxBy - yyBzxBxx - yyBzxByy, -xBzyBy - xyBzyBxx - xyBzyByy, 
  ByBxx + ByByy + yBxxBxx + 2*yBxxByy + yByyByy, 
  BxBy + xByBxx + xByByy + xyBxxBxx + 2*xyBxxByy + xyByyByy + yBxBxx + 
   yBxByy, ByBy + 2*yByBxx + 2*yByByy + yyBxxBxx + 2*yyBxxByy + yyByyByy, 
  -BztBy - yBztBxx - yBztByy, Gtx, Gty, Ht + xGtx, Ht + yGty, yGtx, xGty, 
  -BztBxx - BztByy, -BztBx - xBztBxx - xBztByy, -BztBy - yBztBxx - yBztByy, 
  Gtt), axis = 0)
    
    return(A)
