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
from scipy import signal

def the_matrix(bx, bxx, bxy, by, byx, byy, bz, bzx, bzy,
               bzt, psf, psfx, psfy, psfxx, psfyy, psfxy):
    '''
    This function will be used to perform the convolutions and construct
    the matrix from which the solutions will be calculated.
    '''
    
    #Constructing the matrix for the LKA algorithm
    G = signal.convolve(np.multiply(bz,bz),psf, mode='same', method='fft') #1        
    GGx = np.multiply(bz,bzx)
    Gx = signal.convolve(GGx,psf, mode='same', method='fft') #2
    xGx = signal.convolve(GGx,psfx, mode='same', method='fft') #3
    yGx = signal.convolve(GGx,psfy, mode='same', method='fft') #4
    GGy = np.multiply(bz,bzy)
    Gy = signal.convolve(GGy,psf, mode='same', method='fft') #5
    xGy = signal.convolve(GGy,psfx, mode='same', method='fft') #6
    yGy = signal.convolve(GGy,psfy, mode='same', method='fft') #7
    Ht = signal.convolve(np.multiply(bzt,bz),psf, mode='same', method='fft') #8
    GGxx = np.multiply(bzx,bzx)
    Gxx = signal.convolve(GGxx,psf, mode='same', method='fft') #9
    GGyy = np.multiply(bzy,bzy)
    Gyy = signal.convolve(GGyy,psf, mode='same', method='fft') #10
    GGxy = np.multiply(bzx,bzy)
    Gxy = signal.convolve(GGxy,psf, mode='same', method='fft') #11
    GGtx = np.multiply(bzt,bzx)
    Gtx = signal.convolve(GGtx,psf, mode='same', method='fft') #12 
    GGty = np.multiply(bzt,bzy)
    Gty = signal.convolve(GGty, psf, mode='same', method='fft') #13
    xGxx = signal.convolve(GGxx,psfx, mode='same', method='fft') #14
    xGyy = signal.convolve(GGyy,psfx, mode='same', method='fft') #15
    xGxy = signal.convolve(GGxy,psfx, mode='same', method='fft') #16
    xGtx = signal.convolve(GGtx,psfx, mode='same', method='fft') #17
    xGty = signal.convolve(GGty,psfx, mode='same', method='fft') #18
    yGxx = signal.convolve(GGxx,psfy, mode='same', method='fft') #19
    yGyy = signal.convolve(GGyy,psfy, mode='same', method='fft') #20
    yGxy = signal.convolve(GGxy,psfy, mode='same', method='fft') #21
    yGtx = signal.convolve(GGtx,psfy, mode='same', method='fft') #22
    yGty = signal.convolve(GGty,psfy, mode='same', method='fft') #23
    xxGxx = signal.convolve(GGxx,psfxx, mode='same', method='fft') #24
    xxGxy = signal.convolve(GGxy,psfxx, mode='same', method='fft') #25
    xxGyy = signal.convolve(GGyy,psfxx, mode='same', method='fft') #26  
    xyGxx = signal.convolve(GGxx,psfxy, mode='same', method='fft') #27
    xyGxy = signal.convolve(GGxy,psfxy, mode='same', method='fft') #28
    xyGyy = signal.convolve(GGyy,psfxy, mode='same', method='fft') #29
    yyGxx = signal.convolve(GGxx,psfyy, mode='same', method='fft') #30
    yyGxy = signal.convolve(GGxy,psfyy, mode='same', method='fft') #31
    yyGyy = signal.convolve(GGyy,psfyy, mode='same', method='fft') #32
    Gtt = signal.convolve(np.multiply(bzt,bzt),psf, mode='same', method='fft') #33
    ###end-dave###
    BxBx = signal.convolve(np.multiply(bx,bx),psf, mode='same', method='fft')
    ByBy = signal.convolve(np.multiply(by,by),psf, mode='same', method='fft')
    BxBy = signal.convolve(np.multiply(bx,by),psf, mode='same', method='fft')
    BzBx = signal.convolve(np.multiply(bz,bx),psf, mode='same', method='fft')
    BzBy = signal.convolve(np.multiply(bz,by),psf, mode='same', method='fft')
    mbxbxx = np.multiply(bx,bxx)
    BxBxx = signal.convolve(mbxbxx,psf, mode='same', method='fft')
    mbxbyy = np.multiply(bx,byy)
    BxByy = signal.convolve(mbxbyy,psf, mode='same', method='fft')
    mbxxbxx = np.multiply(bxx,bxx)
    BxxBxx = signal.convolve(mbxxbxx,psf, mode='same', method='fft')
    mbyybyy = np.multiply(byy,byy)
    ByyByy = signal.convolve(mbyybyy,psf, mode='same', method='fft')
    mbxxbyy = np.multiply(bxx,byy)
    BxxByy = signal.convolve(mbxxbyy,psf, mode='same', method='fft')
    mbybxx = np.multiply(by,bxx)
    ByBxx = signal.convolve(mbybxx,psf, mode='same', method='fft')
    mbybyy = np.multiply(by,byy)
    ByByy = signal.convolve(mbybyy,psf, mode='same', method='fft')
    mbzbxx = np.multiply(bz,bxx)
    BzBxx = signal.convolve(mbzbxx,psf, mode='same', method='fft')
    mbzbyy = np.multiply(bz,byy)
    BzByy = signal.convolve(mbzbyy,psf, mode='same', method='fft')
    mbztbxx = np.multiply(bzt,bxx)
    BztBxx = signal.convolve(mbztbxx,psf, mode='same', method='fft')
    mbztbyy = np.multiply(bzt,byy)
    BztByy = signal.convolve(mbztbyy,psf, mode='same', method='fft')
    mbzxbx = np.multiply(bzx,bx)
    BzxBx = signal.convolve(mbzxbx,psf, mode='same', method='fft')
    mbzxby = np.multiply(bzx,by)
    BzxBy = signal.convolve(mbzxby,psf, mode='same', method='fft')
    mbzxbxx = np.multiply(bzx,bxx)
    BzxBxx = signal.convolve(mbzxbxx,psf, mode='same', method='fft')
    mbzxbyy = np.multiply(bzx,byy)
    BzxByy = signal.convolve(mbzxbyy,psf, mode='same', method='fft')
    mbzybx = np.multiply(bzy,bx)
    BzyBx = signal.convolve(mbzybx,psf, mode='same', method='fft')
    mbzyby = np.multiply(bzy,by)
    BzyBy = signal.convolve(mbzyby,psf, mode='same', method='fft')
    mbzybxx = np.multiply(bzy,bxx)
    BzyBxx = signal.convolve(mbzybxx,psf, mode='same', method='fft')
    mbzybyy = np.multiply(bzy,byy)
    BzyByy = signal.convolve(mbzybyy,psf, mode='same', method='fft')
    BztBx = signal.convolve(np.multiply(bzt,bx),psf, mode='same', method='fft')
    BztBy = signal.convolve(np.multiply(bzt,by),psf, mode='same', method='fft')   
    xBzxBx = signal.convolve(mbzxbx,psfx, mode='same', method='fft')
    xBzxBy = signal.convolve(mbzxby,psfx, mode='same', method='fft')
    xBzyBx = signal.convolve(mbzybx,psfx, mode='same', method='fft')
    xBzyBy = signal.convolve(mbzyby,psfx, mode='same', method='fft')
    yBzyBx = signal.convolve(mbzybx,psfy, mode='same', method='fft')
    yBzyBy = signal.convolve(mbzyby,psfy, mode='same', method='fft')
    yBzxBx = signal.convolve(mbzxbx,psfy, mode='same', method='fft')
    yBzxBy = signal.convolve(mbzxby,psfy, mode='same', method='fft')
    yBxBxx = signal.convolve(mbxbxx,psfy, mode='same', method='fft')
    yBxByy = signal.convolve(mbxbyy,psfy, mode='same', method='fft')
    yByBxx = signal.convolve(mbybxx,psfy, mode='same', method='fft')
    yByByy = signal.convolve(mbybyy,psfy, mode='same', method='fft')
    xByBxx = signal.convolve(mbybxx,psfx, mode='same', method='fft')
    xByByy = signal.convolve(mbybyy,psfx, mode='same', method='fft')
    xBzxBxx = signal.convolve(mbzxbxx,psfx, mode='same', method='fft')
    xBzxByy = signal.convolve(mbzxbyy,psfx, mode='same', method='fft')
    yBzxBxx = signal.convolve(mbzxbxx,psfy, mode='same', method='fft')
    yBzxByy = signal.convolve(mbzxbyy,psfy, mode='same', method='fft')
    xBxxBxx = signal.convolve(mbxxbxx,psfx, mode='same', method='fft')
    xBxxByy = signal.convolve(mbxxbyy,psfx, mode='same', method='fft')
    xByyByy = signal.convolve(mbyybyy,psfx, mode='same', method='fft')
    yBxxBxx = signal.convolve(mbxxbxx,psfy, mode='same', method='fft')
    yBxxByy = signal.convolve(mbxxbyy,psfy, mode='same', method='fft')
    yByyByy = signal.convolve(mbyybyy,psfy, mode='same', method='fft')
    xBxBxx = signal.convolve(mbxbxx,psfx, mode='same', method='fft')
    xBxByy = signal.convolve(mbxbyy,psfx, mode='same', method='fft')
    xBzBxx = signal.convolve(mbzbxx,psfx, mode='same', method='fft')
    xBzByy = signal.convolve(mbzbyy,psfx, mode='same', method='fft')
    xBztBxx = signal.convolve(mbztbxx,psfx, mode='same', method='fft')
    xBztByy = signal.convolve(mbztbyy,psfx, mode='same', method='fft')
    yBztBxx = signal.convolve(mbztbxx,psfy, mode='same', method='fft')
    yBztByy = signal.convolve(mbztbyy,psfy, mode='same', method='fft')
    xyBxxBxx = signal.convolve(mbxxbxx,psfxy, mode='same', method='fft')
    xyBxxByy = signal.convolve(mbxxbyy,psfxy, mode='same', method='fft')
    xyByyByy = signal.convolve(mbyybyy,psfxy, mode='same', method='fft')
    xyBzxBxx = signal.convolve(mbzxbxx,psfxy, mode='same', method='fft')
    xyBzxByy = signal.convolve(mbzxbyy,psfxy, mode='same', method='fft')
    xyBzyBxx = signal.convolve(mbzybxx,psfxy, mode='same', method='fft')
    xyBzyByy = signal.convolve(mbzybyy,psfxy, mode='same', method='fft')
    yBzBxx = signal.convolve(mbzbxx,psfy, mode='same', method='fft')
    yBzByy = signal.convolve(mbzbyy,psfy, mode='same', method='fft')
    xBzyBxx = signal.convolve(mbzybxx,psfx, mode='same', method='fft')
    xBzyByy = signal.convolve(mbzybyy,psfx, mode='same', method='fft')
    yBzyBxx = signal.convolve(mbzybxx,psfy, mode='same', method='fft')
    yBzyByy = signal.convolve(mbzybyy,psfy, mode='same', method='fft')
    xxBxxBxx = signal.convolve(mbxxbxx,psfxx, mode='same', method='fft')
    xxBxxByy = signal.convolve(mbxxbyy,psfxx, mode='same', method='fft')
    xxByyByy = signal.convolve(mbyybyy,psfxx, mode='same', method='fft')
    xxBzxBxx = signal.convolve(mbzxbxx,psfxx, mode='same', method='fft')
    xxBzyBxx = signal.convolve(mbzybxx,psfxx, mode='same', method='fft')
    xxBzxByy = signal.convolve(mbzxbyy,psfxx, mode='same', method='fft')
    xxBzyByy = signal.convolve(mbzybyy,psfxx, mode='same', method='fft')
    yyBxxBxx = signal.convolve(mbxxbxx,psfyy, mode='same', method='fft')
    yyBxxByy = signal.convolve(mbxxbyy,psfyy, mode='same', method='fft')
    yyByyByy = signal.convolve(mbyybyy,psfyy, mode='same', method='fft')
    yyBzyBxx = signal.convolve(mbzybxx,psfyy, mode='same', method='fft')
    yyBzyByy = signal.convolve(mbzybyy,psfyy, mode='same', method='fft')
    yyBzxBxx = signal.convolve(mbzxbxx,psfyy, mode='same', method='fft')
    yyBzxByy = signal.convolve(mbzxbyy,psfyy, mode='same', method='fft')    

    #stacking terms
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
  BxBy + xByBxx + xByByy + xyBxxBxx + 2*xyBxxByy + xyByyByy + yBxBxx + yBxByy,
 -BztBx - xBztBxx - xBztByy, -BzxBy - yBzxBxx - yBzxByy, 
  -BzyBy - yBzyBxx - yBzyByy, -BzBy - xBzxBy - xyBzxBxx - xyBzxByy - yBzBxx - yBzByy,
 -BzBy - yBzBxx - yBzByy - yBzyBy - yyBzyBxx - yyBzyByy, 
  -yBzxBy - yyBzxBxx - yyBzxByy, -xBzyBy - xyBzyBxx - xyBzyByy, 
  ByBxx + ByByy + yBxxBxx + 2*yBxxByy + yByyByy, 
  BxBy + xByBxx + xByByy + xyBxxBxx + 2*xyBxxByy + xyByyByy + yBxBxx + yBxByy,
  ByBy + 2*yByBxx + 2*yByByy + yyBxxBxx + 2*yyBxxByy + yyByyByy, 
  -BztBy - yBztBxx - yBztByy, Gtx, Gty, Ht + xGtx, Ht + yGty, yGtx, xGty, 
  -BztBxx - BztByy, -BztBx - xBztBxx - xBztByy, -BztBy - yBztBxx - yBztByy, 
  Gtt), axis = 0)
    
    return(A)
