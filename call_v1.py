#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code represents my pre-call for dave4vm algorithm.
Here data is setup to serve as an entry to the actual code that will call dave4vm
which is do_dave4vm_and.py

Here is where one would want to decide what values of the magnetic field should 
be taken into the variables.


####################################
Dá pra guardar np.array no sqlite!!!
https://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
####################################


@author: andrechicrala
"""

#calling the set of relevant 3rd packages
#from astropy.io import fits
import numpy as np

#calling my set of packages.
#can also be done by: from pydave4vm import *
from pydave4vm import dave4vm
#from pydave4vm import odiffxy5
#from pydave4vm import dave4vm_matrix
from pydave4vm import cubitos
from pydave4vm import do_dave4vm_and
#from pydave4vm import mockdata
#from pydave4vm import and_plot as ap


###testing if the packages were properly imported
dave4vm.dave4vmpy_test_import()
do_dave4vm_and.test_import()
#mockdata.test_import()
cubitos.test_import()
###


#defining a dx and dy in km based on HMI resolution
dx = 1000.00
dy = dx


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

#checking the face of my beloved AR
#this line of code should be removed later
#ap.simples_plot(bx_start)


#Defining a dt in seconds
#In the original dave4vm dt is defined by subtracting the timestamp of the images
#This will be already done when the datacubes are formed and therefore should
#be called as something of the type: dt = dt(i)
dt = 720.00

#Calling do_dave4vm_and 
#the number is the windowsize
magvm, vel4vm, trc = do_dave4vm_and.do_dave4vm(dt,bx_stop,bx_start,by_stop,
                          by_start,bz_stop,bz_start,dx,dy,20)




