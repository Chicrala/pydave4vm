# !/usr/bin/env python3
#  -*- coding: utf-8 -*-
"""
2018-05-25
This code is responsible for downloading the datasets to be used by pydave4vm.

@author: andrechicrala
"""

# fido is the sunpy package responsible for downloads
import drms
import os
import glob
from pydave4vm.addons import stdconfig
from datetime import datetime, timedelta
from sunpy.net import Fido, attrs as a
import astropy.units as a

def check_missing_files(harpnum, directory, requests):
    '''
    This function will check if all the files in a request were properly 
    downloaded to the directory.
    '''    
    # Creating the client instance
    client = drms.Client(email='andrechicrala@gmail.com', verbose=True)
    
    # Filtering the series.
    client.series(r'hmi\.sharp_cea_720s')
    
    # Making three attempts to get the missing data.
    for i in range(3):
        # Comparing the search result and how many files were downloaded.
        if len(requests.data['filename']) != len(glob.glob(directory+'*.fits')):
                print('The number of files downloaded do not match with the search results.')
                
                # Checking which files are missing.
                missing_files = [file for file in requests.data['filename'] if file not in glob.glob(directory+'*.fits')]
        else:
            print(f'No missing files.')
            missing_files = []
        
        # Attempting to download the missing files.
        print('Trying to download the remaining files')
        for file in missing_files:
            # Printing the file name.
            print(f'Missing file: {file}')
            
            # Getting the segment.
            segment = file[44:46]

            # Creating a datetime object to subtract the 12min interval.
            date = datetime.strptime(file[24:39], '%Y%m%d_%H%M%S') - timedelta(minutes=6)

            # Querying again.
            ds = 'hmi.sharp_cea_720s['+str(harpnum)+']['+date.strftime('%Y-%m-%d')+'_'+date.strftime('%H:%M:%S')+'_TAI/'+'0.25h'+'@'+'720s'+']{'+segment+'}'
                
            # Printing ds.
            print(f'Query string: {ds}')

            # Requesting the missing data.
            requests = client.export(ds, method = 'url', protocol = 'fits')
                
            # Getting the request.
            requests.download(directory)
            
            # Creating a list of the downloaded files.
            files = [x.replace(directory,'') for x in glob.glob(directory+'*.fits')]
                
            # Checking if the file is there.
            if file not in files:
                print(f'File {file} NOT downloaded.')
            
            else:
                print(f'File {file} downloaded.')
                
            # Getting rid of possible.
            for file in glob.glob(directory+'*.fits.*'):
                os.remove(file)
    
    return(missing_files)

def downdrms(harpnum, tstart, extent, cadence, out_dir=None):
    '''
    Unlike the previous function, this one uses the drms module:
        
    https://drms.readthedocs.io/en/stable/intro.html
    
    This function takes the harp number assigned to an AR and the initial and
    final time desired to fetch the data from a 'hmi.sharp_cea_720s' data 
    series.
    
    The format for tstart is: '2014-01-01T00:00:00' or '2016.05.18_00:00:00'.
    
    The Harp number will be converted to a string within the code.
    It will then download the magnetic field vector in cilindrical components.
    '''
    
    # Checking path
    if out_dir is None:
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
    ds = 'hmi.sharp_cea_720s['+ str(harpnum) + ']['+ tstart+'_TAI/' + extent + '@' + cadence +']{Br, Bp, Bt}'
    
    # Creating the request object it contains the query id and status.
    requests = client.export(ds, method = 'url', protocol = 'fits')
    
    # Getting the request.
    requests.download(out_dir)
    
    # Checking missing data.
    #missing_files = check_missing_files(harpnum=harpnum, directory=out_dir, requests=requests)
            
    # Feedback.
    print('Downloads complete!')
    
    return(out_dir)#, missing_files)
    
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

###############################################################################
# Code to check the files that were already downloaded.
def flagship(path, download=False):
    '''
    This function will check the downloaded files and flag where a time
    interval is larger than 12 min and download the files if requested.
    '''
    
    # Getting the HARP number.
    harpnum = path[-4:]
    
    # Listing the files.
    files = [file[len(path)+1:] for file in glob.glob(path+'/*Br.fits')]
    
    # Making the timestamps.
    stamps = [datetime.strptime(file[24:39], '%Y%m%d_%H%M%S') for file in files]
    
    # Creating a results storage.
    flags = []
    
    # Checking the time differences between the files.
    for i in range(1,len(stamps)):
        # Flagging the differences if it is larger than 13 minutes. It will 
        # print and append the End/Start time, the gap between then and how 
        # many files should be between them.
        if stamps[i]-stamps[i-1] > timedelta(minutes=12):
            print(stamps[i], stamps[i-1], stamps[i]-stamps[i-1], 
                  (stamps[i]-stamps[i-1])/timedelta(minutes=12))
            flags.append([stamps[i].strftime("%Y.%m.%d_%H:%M:%S"), 
                          stamps[i-1].strftime("%Y.%m.%d_%H:%M:%S"), 
                          stamps[i]-stamps[i-1],
                          (stamps[i]-stamps[i-1])/timedelta(minutes=12)])
    
    # Downloading files if requested.
    if download is True:
        for entry in flags:
            downdrms(harpnum=harpnum, tstart=entry[1], 
                     extent=str(entry[2].seconds/3600)+'h', cadence='720s',
                     out_dir='/Users/andrechicrala/Downloads/test/downtest/')
            #break

    return(flags)


if __name__ == "__main__":
    '''
    The testing zone
    '''
    
    # downdrms(6063, '2015-11-04T00:00:00', '2015-11-04T02:00:00')
    #downdrms(5724, '2013.04.24_00:00:00', '30d', '720s', 
    #         out_dir='/Volumes/DATABASE/data/5724/')
    
    path = '/Volumes/chicrala/data/6063'
    sheep = flagship(path, download=True)
