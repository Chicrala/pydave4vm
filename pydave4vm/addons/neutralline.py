#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code open my config files to fetch the base values specified to run
a code (pydave4vm at the moment).

@author: andrechicrala
"""
import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter

def PIL(bz, gaussian=False, fwhm_pix=40, threshold=150):
    '''
    This function will map the neutral line for a given
    observation in the database.
    '''
    
    # Convolving the array. A masked array of zeros and ones will be produced
    # with (bz > 150).astype(int).
    bz_positive = signal.convolve((bz > threshold).astype(float), np.ones((9,9)),
                                  mode='same', method='fft')
    
    bz_negative = signal.convolve((bz < -1*threshold).astype(float), np.ones((9,9)),
                                  mode='same', method='fft')
    
    # Adding a clipped version off the convolved signals.
    pil_mask = (np.add((bz_positive > 0.5).astype(float),
                   (bz_negative > 0.5).astype(float)) > 1.5).astype(float)
    
    # Checking if a gaussian broadening was requested.
    if gaussian == True:
        # Harcoded stuff.
        sigma = fwhm_pix/2.3548
        
        # Creating the gaussian broadening filter along the PILs.
        pil_gb_map = gaussian_filter(pil_mask, sigma, order=0)
        
        return(pil_gb_map)
        
    return(pil_mask)

if __name__ == '__main__':
    '''
    test zone!
    '''