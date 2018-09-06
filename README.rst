pydave4vm
=========

.. image:: https://img.shields.io/pypi/v/pydave4vm.svg
    :target: https://pypi.python.org/pypi/pydave4vm
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal.png
   :target: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal
   :alt: Latest Travis CI build status

An attempt to make a working version in python of the dave4vm software that was originally written in IDL. 

This work is an attempt to reproduce the differential affine velocity estimator for vector magnetograms (DAVE4VM) developed by
dr. P.W. Shuck. At first this work was published in The Astrophysical Journal 683:1134Y1152, 2008 August 20 - 
TRACKING VECTOR MAGNETOGRAMS WITH THE MAGNETIC INDUCTION EQUATION - P.W. Shuck.

At first, it would be ideal to translate the algorithm as close as possible from IDL to python which is what this first 
version (2018-02-12) aims to do. Once the results are considered reliable, the main objective will be to optimize the code 
and also make it more user friendly.

The goal of this work is not only to re-design an existing tool to better suit the needs of my current work but also to 
ultimately deliver a tool that can be used by the solar physics community for free.

Currently, the version within the Jupyter Notebook was already tested for some magnetograms and is capable of reproducing
the IDL version results.

---------------------------------------

Description of the modules:
- call_v1.py: This module organize the fits using the cubitos.py module and should be, when the code is properly done, 
where the user will interact with the algorithm to personalize the size of the spatial grid, time difference and what data 
will be used.

- cubitos.py: This module scan a folder for the Br, Btheta, Bphi .fits files and create data cubes with them.

- do_dave4vm_and.py: Here data is pre-processed to be fed on the dave4vm call using the odiffxy.py module and calculating
averages between the .fits files. This module returns the dictionary with the variables that are fed into dave4vm.py 
(magvm), the velocities calculated with dave4vm (vel4vm) and the trace of the main matrix used to perform the calculations 
(trc).

- odiffxy5.py: This module will calculate the spatial derivatives of dx and dy and return those results to the
do_dave4vm_and.py module.

- dave4vm.py: In this module the main calculations are done. At first the kernel that will be used to calculate 
the convolution integrals in the dave4vm_matrix.py module is created. Then, the output matrix (AM) is used to calculate the
velocities leading to the final product (vel4vm).

-dave4vm_matrix.py: This module calculates the convolution integrals between the data stored in the dictionary (magvm) and 
the kernel (psf, psfx, psfy, psfxx, psfyy, psfxy)

---------------------------------------

Changes:
2018-02-12: The first working version was added on this repository. 
It was written in a way that is as faithful as possible to the original code.
Testing and comparing the performance of this version against the original code is ongoing.

2018-01-05: Ipython notebook and test data added. Some bugs were corrected but the major problems still persists.

2018-05-10: New Ipython notebook added with a working version.

2018-05-24: Scipy.signal convolve and numpy solve introduced improving the code speed.

---------------------------------------

Original License:

AUTHORIZATION TO USE AND DISTRIBUTE

I hereby agree to the following terms governing the use and
redistribution of the DAVE/DAVE4VM software release originally written and
developed by Dr. Schuck.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that (1) source code
distributions retain this paragraph in its entirety, (2) distributions
including binary code include this paragraph in its entirety in the
documentation or other materials provided with the distribution, (3)
improvements, additions and upgrades to the software will be provided
to NRL Authors in computer readable form, with an unlimited,
royalty-free license to use these improvements, additions and
upgrades, and the authority to grant unlimited royalty-free
sublicenses to these improvements and (4) all published research using
this software display the following acknowledgment ``This work uses
the DAVE/DAVE4VM codes written and developed by the Naval Research
Laboratory.''

Neither the name of NRL or its contributors, nor any entity of the
United States Government may be used to endorse or promote products
derived from this software, nor does the inclusion of the NRL written
and developed software directly or indirectly suggest NRL's or the
United States Government's endorsement of this product.

THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

---------------------------------------

Link for download the original code written in IDL:
https://ccmc.gsfc.nasa.gov/lwsrepository/index.php
