#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module takes both the results from pydave4vm (the photospheric velocities) 
and the magnetic field components to calculate the pointing flux
of each pixel and also the integral of these values on the image.

There is also a function to calculate the absolute velocities from a data
set at the bottom.

@author: andrechicrala
"""
import numpy as np

def poyntingflux(dx, Bx, By, Bz, Vx, Vy, Vz):
    '''
    In this function the following steps are taken:
        - the adjust (cgs - SI) constants are defined;
        - the magnetic field is transformed to SI units;
        - the velocity is transformed to SI units;
        - calculate the normal energy flux;
        - calculate the tangential energy flux;
        - calculate the sum of both normal and tangential contributions;
        - calculate the integral of all three quantities calculated above.
    '''
    # Constants to adjust to SI
    adj_B = 1e-4 # Adjust magnetic field from Gauss to Tesla
    adj_V = 1e3 # Adjust velocity from km/s to m/s
    mu = np.multiply(4e-7,np.pi) #Vacuum permeability
    
    # Since dx was given in km this step transform it to m and calculate the 
    # pixel area.
    adj_px = np.power(dx*1000,2)
    
    # Adjusting to SI.
    Bx = np.multiply(Bx,adj_B)
    By = np.multiply(By,adj_B)
    Bz = np.multiply(Bz,adj_B)
    Vx = np.multiply(Vx,adj_V)
    Vy = np.multiply(Vy,adj_V)
    Vz = np.multiply(Vz,adj_V)
    
    # Calculating the normal energy flux.
    Sn = np.multiply(np.divide(np.multiply((np.power(Bx,2) + np.power(By,2)),
                                           Vz),mu), adj_px)
    
    # Calculating the tangential energy flux.
    # The -1 multiplication is due to the orientation of By and Bp.
    St = np.multiply(np.divide(np.multiply(np.multiply(np.multiply(Vx,Bx) \
                                                       + np.multiply(Vy,By),
                                                       Bz),-1),mu), adj_px)
    
    # Summing the contributions from normal and tangenrial components.
    Ss = np.add(Sn,St)
    
    # Integrating over the image space.
    int_Sn = np.sum(Sn)
    int_St = np.sum(St)
    int_Ss = np.sum(Ss)
    
    return(Sn, St, Ss, int_Sn, int_St, int_Ss)

def poyntingflux_cgs(Bx: np.array, By: np.array, Bz: np.array, 
                     Vx: np.array, Vy: np.array, Vz: np.array):
    '''
    This version is also faster.
    In this function the following steps are taken:
        - Surrender to the CGS system;
        - calculate the normal energy flux;
        - calculate the tangential energy flux;
        - calculate the sum of both normal and tangential contributions;
        - calculate the integral of all three quantities calculated above.
    '''
    # Adjust velocity from km/s to cm/s.
    adj_V = 1e5
    
    # Adjusting to SI.
    Vx = Vx*adj_V
    Vy = Vy*adj_V
    Vz = Vz*adj_V
    
    # Calculating the normal energy flux.
    Sn = ((Bx*Bx + By*By)*Vz)/(4*np.pi)
    
    # Calculating the tangential energy flux.
    # The -1 multiplication is due to the orientation of By and Bp.
    St = -1.*((Vx*Bx + Vy*By)*Bz)/(4*np.pi)
    
    # Summing the contributions from normal and tangenrial components.
    Ss = Sn+St

    # Integrating over the image space.
    int_Sn = np.sum(Sn)
    int_St = np.sum(St)
    int_Ss = np.sum(Ss)
    
    return(Sn, St, Ss)














