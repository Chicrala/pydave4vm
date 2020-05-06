#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module filters the velocities calculated by PyDAVE4VM.

@author: andrechicrala
"""
import numpy as np

def Vperp(bx: np.array, by: np.array, bz: np.array, 
          vx: np.array, vy: np.array, vz: np.array):
    # Calculating the dot product and dividing by B squared.
    fraction = -1*((vx*bx+vy*by+vz*bz)/(bx*bx+by*by+bz*bz))
    
    # Now we calculate V perpendicular.
    vpx = vx+fraction*bx
    vpy = vy+fraction*by
    vpz = vz+fraction*bz
    
    return(vpx,vpy,vpz)
    