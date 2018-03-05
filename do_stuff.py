#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Function to automate my analysis a bit

@author: andrechicrala
"""
import numpy as np
from pydave4vm import call_v1
from and_mods import ler_organizar
from and_mods import filtro
#from and_mods import and_plot as ap
import time


###Obtaining the dataset###
def obtain_data_set():
    #executing pydave4vm
    magvm, vel4vm, trc, kernel = call_v1.call_v1()
    
    #taking the idl results for comparissom
    idl_results = ler_organizar.arrumando_dados()
    
    #making the subtractions with and without filter
    idl_m_py, idl_m_py_fil = ler_organizar.comparando_dics(idl_results, vel4vm)
    
    return(magvm, vel4vm, trc, kernel, idl_results, idl_m_py, idl_m_py_fil)
###########################

###Processing data###
#this function takes each image on the two dictionaries that are returned from
#obtain_data_set and do some operations with them returning 5 new dictionaries
#when the operations with idl no longer become necessary a newer version 
#without it will be build.
def process_data_set(vel4vm, idl_results, idl_min_py, idl_min_py_fil):
    #defining a set of keys
    keys = ['U0', 'UX', 'UY',
            'V0', 'VX', 'VY',
            'W0', 'WX', 'WY']
    
    
    #discovering extreme points location in the python results and
    #also the idl nans
    #creating an empty dictionary to hold the results
    #to hold the results of vel4vm filtered with filtro.py 'filtro.media'
    vel4vm_filt_avg = {}
    vel4vm_filt_avg_abs = {}
    #to map where lies the extreme values of python
    py_ext_values = {}
    #to map where lies the NANs of idl
    idl_nans = {}
    #to hold the results of the subtraction between the results of idl and 
    #python
    #idl_min_py = {}
    #to hold the results of the subtraction between the results of idl and 
    #the filtered results of python
    #idl_min_py_fil = {}
    
    #dictionaries to fit some statistical properties of the fits
    #the names of the dictionaries only add to the beggining what kind of 
    #operation is being done on the following dictionary
    #mean
    mean_vel4vm = {}
    mean_idl_results = {}
    mean_vel4vm_filt_avg = {}
    mean_vel4vm_filt_avg_abs = {}
    mean_idl_min_py = {}
    mean_idl_min_py_fil = {}
    
    #variance
    var_vel4vm = {}
    var_idl_results = {}
    var_vel4vm_filt_avg = {}
    var_vel4vm_filt_avg_abs = {}
    var_idl_min_py = {}
    var_idl_min_py_fil = {}
    
    #standard deviation
    std_vel4vm = {}
    std_idl_results = {}
    std_vel4vm_filt_avg = {}
    std_vel4vm_filt_avg_abs = {}
    std_idl_min_py = {}
    std_idl_min_py_fil = {}
    
    #defining the filter value to be inserted on filtro.py
    filter_value = 10
    
    for i in range(0,len(keys)):
        
        #using the functions in filtro to process the correspondent values
        #defined by the keys argument
        vel4vm_filt_avg[keys[i]] = filtro.filtro_media(vel4vm[keys[i]], filter_value)
        #testing the new filters here
        vel4vm_filt_avg_abs[keys[i]] = filtro.filtro_media_abs2(vel4vm[keys[i]], filter_value)
        py_ext_values[keys[i]] = filtro.identificar_extremos(vel4vm[keys[i]], filter_value)
        idl_nans[keys[i]] = filtro.identificar_nans(idl_results[keys[i]])
        
        #taking the statistics of the created datasets
        #mean
        mean_vel4vm[keys[i]] = np.mean(vel4vm[keys[i]])
        mean_idl_results[keys[i]] = np.mean(idl_results[keys[i]][~np.isnan(idl_results[keys[i]])])
        mean_vel4vm_filt_avg[keys[i]] = np.mean(vel4vm_filt_avg[keys[i]])
        mean_vel4vm_filt_avg_abs[keys[i]] = np.mean(vel4vm_filt_avg_abs[keys[i]])
        mean_idl_min_py[keys[i]] = np.mean(idl_min_py[keys[i]][~np.isnan(idl_min_py[keys[i]])])
        mean_idl_min_py_fil[keys[i]] = np.mean(idl_min_py_fil[keys[i]][~np.isnan(idl_min_py_fil[keys[i]])])
        
        #variance
        var_vel4vm[keys[i]] = np.var(vel4vm[keys[i]])
        var_idl_results[keys[i]] = np.var(idl_results[keys[i]][~np.isnan(idl_results[keys[i]])])
        var_vel4vm_filt_avg[keys[i]] = np.var(vel4vm_filt_avg[keys[i]])
        var_vel4vm_filt_avg_abs[keys[i]] = np.var(vel4vm_filt_avg_abs[keys[i]])
        var_idl_min_py[keys[i]] = np.var(idl_min_py[keys[i]][~np.isnan(idl_min_py[keys[i]])])
        var_idl_min_py_fil[keys[i]] = np.var(idl_min_py_fil[keys[i]][~np.isnan(idl_min_py_fil[keys[i]])])
        
        #standard deviation
        std_vel4vm[keys[i]] = np.std(vel4vm[keys[i]])
        std_idl_results[keys[i]] = np.std(idl_results[keys[i]][~np.isnan(idl_results[keys[i]])])
        std_vel4vm_filt_avg[keys[i]] = np.std(vel4vm_filt_avg[keys[i]])
        std_vel4vm_filt_avg_abs[keys[i]] = np.std(vel4vm_filt_avg_abs[keys[i]])
        std_idl_min_py[keys[i]] = np.std(idl_min_py[keys[i]][~np.isnan(idl_min_py[keys[i]])])
        std_idl_min_py_fil[keys[i]] = np.std(idl_min_py_fil[keys[i]][~np.isnan(idl_min_py_fil[keys[i]])])

    return(vel4vm_filt_avg, vel4vm_filt_avg_abs, py_ext_values, idl_nans,\
           mean_vel4vm, mean_idl_results, mean_vel4vm_filt_avg, mean_vel4vm_filt_avg_abs,\
           mean_idl_min_py, mean_idl_min_py_fil, var_vel4vm, var_idl_results, \
           var_vel4vm_filt_avg, var_vel4vm_filt_avg_abs, var_idl_min_py, var_idl_min_py_fil,\
           std_vel4vm, std_idl_results, std_vel4vm_filt_avg, std_vel4vm_filt_avg_abs, std_idl_min_py,\
           std_idl_min_py_fil)


#call to execute some of the functions above
def executar():
    
    #this bit here should create all the relevant dictionaries
    magvm, vel4vm, trc, kernel, idl_results, idl_m_py, idl_m_py_fil = obtain_data_set()
    
    #here the data obtained from the dictionaries should be processed
    vel4vm_filt_avg, vel4vm_filt_avg_abs, py_ext_values, idl_nans, \
    mean_vel4vm, mean_idl_results, mean_vel4vm_filt_avg, mean_vel4vm_filt_avg_abs, mean_idl_min_py,\
    mean_idl_min_py_fil, var_vel4vm, var_idl_results, var_vel4vm_filt_avg, var_vel4vm_filt_avg_abs,\
    var_idl_min_py, var_idl_min_py_fil, std_vel4vm, std_idl_results,\
    std_vel4vm_filt_avg, std_vel4vm_filt_avg_abs, std_idl_min_py,\
    std_idl_min_py_fil = process_data_set(vel4vm, idl_results, 
                                          idl_m_py, idl_m_py_fil)
    
    #returning everything that was obtained with this code.
    return(magvm, vel4vm, trc, kernel, idl_results, idl_m_py, idl_m_py_fil,\
           vel4vm_filt_avg, vel4vm_filt_avg_abs, py_ext_values, idl_nans, \
           mean_vel4vm, mean_idl_results, mean_vel4vm_filt_avg, mean_vel4vm_filt_avg_abs,\
           mean_idl_min_py, mean_idl_min_py_fil, var_vel4vm, var_idl_results,\
           var_vel4vm_filt_avg, var_vel4vm_filt_avg_abs, var_idl_min_py, var_idl_min_py_fil,\
           std_vel4vm, std_idl_results, std_vel4vm_filt_avg, std_vel4vm_filt_avg_abs, std_idl_min_py,\
           std_idl_min_py_fil)

#initial time
t0 = time.time()

#take a deep breath, press play and go for a walk =)
magvm, vel4vm, trc, kernel, idl_results, idl_m_py, idl_m_py_fil,\
vel4vm_filt_avg, vel4vm_filt_avg_abs, py_ext_values, idl_nans, \
mean_vel4vm, mean_idl_results, mean_vel4vm_filt_avg, mean_vel4vm_filt_avg_abs,\
mean_idl_min_py, mean_idl_min_py_fil, var_vel4vm, var_idl_results,\
var_vel4vm_filt_avg, var_vel4vm_filt_avg_abs, var_idl_min_py, var_idl_min_py_fil,\
std_vel4vm, std_idl_results, std_vel4vm_filt_avg, std_vel4vm_filt_avg_abs, std_idl_min_py,\
std_idl_min_py_fil = executar()

#end time
t1 = time.time()

#total execution time
total = t1 - t0












