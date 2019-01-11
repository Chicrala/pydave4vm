#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This algorithm should be run after the downloads are complete to check 
if the timestamps are consistent with each other. This way it will avoid
misscalculations that may happen if some files are not downloaded.


@author: andrechicrala
"""

import glob
import os
    
def check_fits(path):
    '''
    This module will list all the fits
    within a directory and group check
    if we have trios with the same 
    timestamp. If they don't, they 
    should be excluded.
    '''
    
    #listing the available data 
    Br_files = sorted(glob.glob(path+'*.Br.fits'))
    Bt_files = sorted(glob.glob(path+'*.Bt.fits'))
    Bp_files = sorted(glob.glob(path+'*.Bp.fits'))
    
    #removing the extensions
    Br_files = [x[:-7] for x in Br_files]
    Bt_files = [x[:-7] for x in Bt_files]
    Bp_files = [x[:-7] for x in Bp_files]
    
    #watching for the intersection
    inter = set(Br_files).intersection(Bt_files, Bp_files)
    
    #keeping the elements not in the intersection
    Br_unique = [ele for ele in Br_files if ele not in inter]
    Bt_unique = [ele for ele in Bt_files if ele not in inter]
    Bp_unique = [ele for ele in Bp_files if ele not in inter]
    
    #restoring the extensions for the unique
    Br_unique = [ele + 'Br.fits' for ele in Br_unique]
    Bt_unique = [ele + 'Bt.fits' for ele in Bt_unique]
    Bp_unique = [ele + 'Bp.fits' for ele in Bp_unique]
    
    #checking if there are mismatched elements
    if Br_unique != []:
        #removing the "extra" itens
        for item in Br_unique:
            print(f'Removing the file: {item}')
            os.remove(item)
            
    #checking if there are mismatched elements
    if Bt_unique != []:
        #removing the "extra" itens
        for item in Bt_unique:
            print(f'Removing the file: {item}')
            os.remove(item)
            
    #checking if there are mismatched elements
    if Bp_unique != []:
        #removing the "extra" itens
        for item in Bp_unique:
            print(f'Removing the file: {item}')
            os.remove(item)
    
    else:
        print('No files to remove.')
    
    return(Br_unique, Bt_unique, Bp_unique)

if __name__ == '__main__':
    '''
    The classical testing zone
    '''
    
    
    path = '/Users/andrechicrala/Downloads/7256/'
    
    check_fits(path)
           