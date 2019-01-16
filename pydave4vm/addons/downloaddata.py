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


def downfido(harpnum, tstart, tend):
    '''
    This function takes the harp number
    assigned to an AR and the initial and
    final time desired to fetch the data
    from a 'hmi.sharp_cea_720s' data series.
    
    The format for tstart and tend is:
        '2014-01-01T00:00:00'
    
    The Harp number will be converted to a
    string within the code.
    
    It will then download the magnetic
    field vector in cilindrical components.
    '''
    # using Fido search to look for results
    res = Fido.search(a.jsoc.Time(tstart, tend),
                      # specifying the data series
                      a.jsoc.Series('hmi.sharp_cea_720s'),
                      # adding my email to be notified
                      # this is mandatory and the email
                      # must be registered with JSOC
                      a.jsoc.Notify('andrechicrala@gmail.com'),
                      # setting the harpnumber as primekey
                      # for this search
                      a.jsoc.PrimeKey('HARPNUM', str(harpnum)),
                      # specifying which segments will be
                      # queried
                      a.jsoc.Segment('Bp') &\
                      a.jsoc.Segment('Bt') &\
                      a.jsoc.Segment('Br'))
    
    # download files showing a progress bar
    Fido.fetch(res, progress = True)
    
    return

def downjsoc(harpnum, tstart, tend, path = None):
    '''
    Unlike the previous function, this one
    uses the Jsoc module from Sunpy.
    
    This function takes the harp number
    assigned to an AR and the initial and
    final time desired to fetch the data
    from a 'hmi.sharp_cea_720s' data series.
    
    The format for tstart and tend is:
        '2014-01-01T00:00:00'
    
    The Harp number will be converted to a
    string within the code.
    
    It will then download the magnetic
    field vector in cilindrical components.
    '''
    
    # checking path
    if path is None:
        pass
    
    # creating the client instance
    client = jsoc.JSOCClient()
    
    # querying
    res = client.search(a.jsoc.Time(tstart, tend),
                      # specifying the data series
                      a.jsoc.Series('hmi.sharp_cea_720s'),
                      # adding my email to be notified
                      # this is mandatory and the email
                      # must be registered with JSOC
                      a.jsoc.Notify('andrechicrala@gmail.com'),
                      # setting the harpnumber as primekey
                      # for this search
                      a.jsoc.PrimeKey('HARPNUM', str(harpnum)),
                      # specifying which segments will be
                      # queried
                      a.jsoc.Segment('Bp') &\
                      a.jsoc.Segment('Bt') &\
                      a.jsoc.Segment('Br'))
    
    # creating the request object
    # it contains the query id and status
    # the data can only be downloaded when status
    # is 0
    requests = client.request_data(res)
    
    # waiting for the query status to change
    while requests.status != 0:
        
        print('Request status: ', requests.status)
        print('Going to sleep...zZz...')
        time.sleep(60)
    
    # getting the request
    res = client.get_request(requests, path = path)
    # adding a progress bar
    res.wait(progress=True)
    
    return

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
    
    # Comparing the search result and how many files were downloaded.
    missing_files = []
    
    # Making three attempts to get the
    for i in range(3):
        if len(requests.data) != len(files):
            print('The number of files downloaded do not match with the search results.')
            
            # Checking which files are missing.
            for file in requests.data['filename']:
                if file not in files:
                    missing_files.append(file)
                    
            # Attempting to download the missing files.
            print('Trying to download the remaining files')
            for file in missing_files:
                # Taking the day stamp of the missing file and re-formatting it.
                daystamp = file[24:28]+'-'+file[28:30]+'-'+file[30:32]
                
                # Taking the hour stamp of the missing file and subtracting 12 min.
                hourstamp = str(int(file[33:39]) - 1200)
        
                # Re-formatting the hourstamp.
                hourstamp = hourstamp[0:2]+':'+hourstamp[2:4]+':'+hourstamp[4:6]
                
                # Querying again.
                ds = 'hmi.sharp_cea_720s['+ str(harpnum)+\
                     ']['+ daystamp+'_'+hourstamp+'_TAI/'+'1h'+'@'+'720s'+']{Br, Bp, Bt}'
                
                # Requesting the missing data.
                requests = client.export(ds, method = 'url', protocol = 'fits')
                
                # Getting the request
                requests.download(directory)
                
                # Checking if the file is there. Removing it from the list if so.
                for file in requests.data['filename']:
                    if file not in glob.glob(directory+file):
                        print(f'File {file} NOT downloaded.')
                        
                    else:
                        # Remove the downloaded file from the missing file list.
                        missing_files.remove(file)
        else:
            print(f'No missing files. Scan: {i}')
    
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
    
    # checking path
    if path is None:
        
        out_dir = '/Users/andrechicrala/Downloads/'+str(harpnum)+'/'
        
        # checking if the path exists
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
    
    # creating the client instance
    client = drms.Client(email = 'andrechicrala@gmail.com', verbose = True)
    
    # filtering the series
    client.series(r'hmi\.sharp_cea_720s')
    
    # querying
    ds = 'hmi.sharp_cea_720s['+ str(harpnum) + \
    ']['+ tstart+'_TAI/' + extent + '@' + cadence +']{Br, Bp, Bt}'
    
    # creating the request object
    # it contains the query id and status
    # the data can only be downloaded when status
    # is 0
    requests = client.export(ds, method = 'url', protocol = 'fits')
    
    # getting the request
    requests.download(out_dir)
    
    # Checking missing data.
    missing_files = check_missing_files(harpnum, out_dir, requests)
            
    # printing
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