# !/usr/bin/env python3
#  -*- coding: utf-8 -*-
"""
2018-05-25
This code is responsible for downloading the datasets to be used by pydave4vm.

@author: andrechicrala
"""

# fido is the sunpy package responsible for downloads
from sunpy.net import Fido, attrs as a
from sunpy.net import jsoc
import drms
import time
import os
import glob
from pydave4vm.addons import stdconfig
from datetime import datetime, timedelta

def missed(requests,directory):
    '''
    Support function to check the directory for the missing files.
    Using this function the missing files variable setting will be
    confined to this namespace.
    '''
    # Comparing the search result and how many files were downloaded.
    missing_files = []
    
    if len(requests.data) != len(glob.glob(directory+'*.fits')):
            print('The number of files downloaded do not match with the search results.')
            
            # Checking which files are missing.
            for file in requests.data['filename']:
                if file not in glob.glob(directory+'*.fits'):
                    missing_files.append(file)
    else:
        print(f'No missing files.')
        missing_files = []

    return(missing_files)

def check_missing_files(harpnum, directory, requests=None, tstart=None, 
                        extent=None, cadence=None):
    '''
    This function will check if all the files in a request were properly 
    downloaded to the directory.
    '''    
    # Creating the client instance
    client = drms.Client(email = 'andrechicrala@gmail.com', verbose = True)
    
    # Filtering the series
    client.series(r'hmi\.sharp_cea_720s')
    
    # Checking if a request was already passed and creating one if not.
    if requests is None:
        # querying
        ds = 'hmi.sharp_cea_720s['+ str(harpnum) + \
        ']['+ tstart+'_TAI/' + extent + '@' + cadence +']{Br, Bp, Bt}'
        
        # creating the request object
        # it contains the query id and status
        # the data can only be downloaded when status
        # is 0
        requests = client.export(ds, method = 'url', protocol = 'fits')
    
    # Creating a list of the downloaded files.
    files = [x.replace(directory,'') for x in glob.glob(directory+'*.fits')]
    
    # Making three attempts to get the
    for i in range(3):
        # Flagging the missing files
        missing_files = missed(requests,directory)
        
        # Attempting to download the missing files.
        print('Trying to download the remaining files')
        for file in missing_files:
            # Printing the file name.
            print(f'Missing file: {file}')

            # Creating a datetime object to subtract the 12min interval.
            date = datetime.strptime(file[24:39], '%Y%m%d_%H%M%S') - timedelta(minutes=12)

            # Querying again.
            ds = 'hmi.sharp_cea_720s['+str(harpnum)+']['+date.strftime('%Y-%m-%d')+'_'+date.strftime('%H:%M:%S')+'_TAI/'+'0.5h'+'@'+'720s'+']{Br, Bp, Bt}'
                
            # Printing ds.
            print(f'Query string: {ds}')

            # Requesting the missing data.
            requests = client.export(ds, method = 'url', protocol = 'fits')
                
            # Getting the request
            requests.download(directory)
                
            # Checking if the file is there.
            if file_ not in glob.glob(directory):
                print(f'File {file_} NOT downloaded.')
            
            # Deleting duplicates.
            for file_ in glob.glob(directory+'*.fits.1'):
                os.remove(file_)
    
    return(missing_files)

def downdrms(harpnum, tstart, extent, cadence, path = None):
    '''
    Unlike the previous function, this one
    uses the drms module:
        
    https://drms.readthedocs.io/en/stable/intro.html
    
    This function takes the harp number
    assigned to an AR and the initial and
    final time desired to fetch the data
    from a 'hmi.sharp_cea_720s' data series.
    
    The format for tstart is:
        '2014-01-01T00:00:00'
        or
        '2016.05.18_00:00:00'
    
    The Harp number will be converted to a
    string within the code.
    
    It will then download the magnetic
    field vector in cilindrical components.
    '''
    
    # Checking path
    if path is None:
        # Defaulting for the hardrive connected on linux.
        out_dir = stdconfig.readconfig('linux','data')+str(harpnum)+'/'
        
        # Checking if the path exists.
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
    
    # Creating the client instance.
    client = drms.Client(email = 'andrechicrala@gmail.com', verbose = True)
    
    # Filtering the series.
    client.series(r'hmi\.sharp_cea_720s')
    
    # Querying.
    ds = 'hmi.sharp_cea_720s['+ str(harpnum) + \
    ']['+ tstart+'_TAI/' + extent + '@' + cadence +']{Br, Bp, Bt}'
    
    # creating the request object it contains the query id and status
    # the data can only be downloaded when status is 0.
    requests = client.export(ds, method = 'url', protocol = 'fits')
    
    # Getting the request.
    requests.download(out_dir)
    
    # Checking missing data.
    missing_files = check_missing_files(harpnum=harpnum, directory=out_dir, requests=requests)
            
    # Feedback.
    print('Downloads complete!')
    
    return(out_dir, missing_files)

def checksegments():
    '''
    This function will print the segments
    of the hmi.sharp_cea_720s series.
    While not directly relevant for the code,
    this will be kept here for future reference.
    '''
    
    # using the client
    c = drms.Client()
    
    # asking for the info
    si = c.info('hmi.sharp_cea_720s')
    
    # printing the info
    print(si.segments.index.values)
    
    return


if __name__ == "__main__":
    '''
    The testing zone
    '''
    
    # downdrms(6063, '2015-11-04T00:00:00', '2015-11-04T02:00:00')
    downdrms(6555, '2016.04.16_00:00:00', '30d', '720s')
