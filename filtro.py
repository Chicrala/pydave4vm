#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code objetive is to filter discrepant numbers within a 2x2 array.
The values can be substituted creating a new 2x2 array according to the 
following options:
    - mean: in this case the new value will be the mean value of the entire 
    matrix; 
    - neighbour cell: in this case the new value will be the same as the next 
    cell;
    - NAN: the number shall be substituted with the flag NAN (not a number);


@author: andrechicrala
"""

###importing packages###
import numpy as np
import copy

#This function receives a dataset and filter the values who are a number of 
#times bigger than the mean value. The entries are then the dataset and the
#amount of times that the mean will be multiplied for comparisson
def filtro_media(data,filtro):
    
    #Copying the data
    new_data = copy.copy(data)
    #Calculating the mean value of the dataset
    mean = np.mean(new_data)
    #Searching where the values deviates n times from the mean
    index = np.where(new_data > filtro * mean)
    index2 = np.where(new_data < -1*filtro * mean)
    
    #Substituting the positive values
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = mean
    #Substituting the negative values
    for i in range(0,len(index2[0])):
        y = index2[0][i]
        x = index2[1][i]        
        new_data[y,x] = -1*mean
    
    
    return(new_data)
    
#This function receives a dataset and filter the values who are a number of 
#times bigger than the mean value of the absolute values. 
#The entries are then the dataset and the
#amount of times that the mean will be multiplied for comparisson    
def filtro_media_abs(data,filtro):
    
    #Copying the data
    new_data = copy.copy(data)
    
    #taking the absolute value
    new_data_abs = np.sqrt(np.multiply(new_data, new_data))
    
    #Calculating the mean value of the dataset
    mean = np.mean(new_data_abs)
    
    #Searching where the values deviates n times from the mean
    index = np.where(new_data_abs > filtro * mean)
    
    #Substituting the positive values
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = 0
        
    #recalculating the mean without the bad values:
    mean2 = np.mean(new_data)
    
    #now substituting by the mean2
    #Substituting the positive values
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = mean2
    
    return(new_data)
    
#This function receives a dataset and filter the values who are a number of 
#times bigger than the mean value of the absolute values.
#The entries are then the dataset and the
#amount of times that the mean will be multiplied for comparisson.
#the mean will be calculated disregarding the values that go to zero which is
#what changes if compared to the previous routine.
def filtro_media_abs2(data,filtro):
    
    #Copying the data
    new_data = copy.copy(data)
    
    #taking the absolute value
    new_data_abs = np.sqrt(np.multiply(new_data, new_data))
    
    #Calculating the mean value of the dataset
    mean = np.mean(new_data_abs)
    
    #Searching where the values deviates n times from the mean
    index = np.where(new_data_abs > filtro * mean)
    
    #Substituting the positive values
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = 0
    
    #here is where the change take place.
    #recalculating the mean without the bad values:
    shape = new_data.shape
    mean2 = np.divide(np.sum(new_data),\
                      np.subtract(np.multiply(shape[0],shape[1]),len(index[0])))
    
    #now substituting by the mean2
    #Substituting the positive values
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = mean2
    
    return(new_data)
    
    
#This function is similar to filtro_media however, this time, the values
#will be replaced by 0 for the ones that satisfy the condition and +-1 for 
#the aberrant values.
def identificar_extremos(data, filtro):
    
    #Copying the data
    new_data = copy.copy(data)
    #Calculating the mean value of the dataset
    mean = np.mean(new_data)
    #Searching where the values deviates n times from the mean
    index = np.where(new_data > filtro * mean)
    index2 = np.where(new_data < -1*filtro * mean)
    #taking the other values
    index3 = np.where(np.logical_and(new_data >= -1*filtro * mean, new_data <= filtro * mean))
    
    #Substituting the positive values
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = 1
    #Substituting the negative values
    for i in range(0,len(index2[0])):
        y = index2[0][i]
        x = index2[1][i]        
        new_data[y,x] = -1
    #substituting the other values:
    for i in range(0, len(index3[0])):
        y = index3[0][i]
        x = index3[1][i]        
        new_data[y,x] = 0
        
    return(new_data)

#Similarly to identificar_extremos, this function will mark where the values
#in the given dataset are nans with +1 and the 'real' values with 0
def identificar_nans(data):
    
    #Copying the data
    new_data = copy.copy(data)
    
    #searching the values
    index = np.where(new_data != new_data)
    index2 = np.where(new_data == new_data)
    
    #Substituting the nans
    for i in range(0,len(index[0])):
        y = index[0][i]
        x = index[1][i]        
        new_data[y,x] = 1
    #Substituting the values
    for i in range(0,len(index2[0])):
        y = index2[0][i]
        x = index2[1][i]        
        new_data[y,x] = 0
    
    
    return(new_data)
    
    
#This function is similar to filtro_media however, this time,
#the values are replaced by the value of a neighbouring cell that is closer to
#the filter value
def filtro_neighbour(data,filtro):
    
    #Copying the data
    new_data = copy.copy(data)
    #Calculating the mean value of the dataset
    mean = np.mean(new_data)
    #Searching where the values deviates n times from the mean
    index = np.where(new_data > filtro * mean)
    index2 = np.where(new_data < -1*filtro * mean)
    #Checking for the dimensions of the data
    dims = np.shape(data)
    
    #Defining the neighbourhood of a pixel
    #thanks to:
    #https://stackoverflow.com/questions/1620940/
    #determining-neighbours-of-cell-two-dimensional-list
    #taking the size of the grid
    X = dims[1]-1
    Y = dims[0]-1
    #defining the neighborhood
    neighbors = lambda y, x : [(y2, x2) for y2 in range(y-1, y+2)
                                   for x2 in range(x-1, x+2)
                                   if (-1 < y <= Y and
                                       -1 < x <= X and
                                       (y != y2 or x != x2) and
                                       (0 <= y2 <= Y) and
                                       (0 <= x2 <= X))]

    #Scanning the pixels where the value is bigger than filtro*mean
    for i in range(0,len(index[0])):
        
        #running for the given pixel
        y = index[0][i]
        x = index[1][i]
        
        #finding the adjacent points
        the_hood = neighbors(y,x)
        
        #creating an empty list to receive the values
        values = []
        #checking which of the neighbourhood values is closer to the average
        for j in range(0, len(the_hood)):
            
            #getting the neighbourhood values
            values.append(new_data[the_hood[j]])
        
        #Selecting and replacing the value that strongly deviates for the
        #neighbour with the closest value to the mean      
        new_data[y,x] = min(values, key=lambda x:abs(x-mean))        
       
    
    #Scanning the pixels where the value is smaller than -filtro*mean
    for a in range(0,len(index2[0])):
        #running for the given pixel
        y = index[0][i]
        x = index[1][i]
        
        #finding the adjacent points
        the_hood = neighbors(y,x)
        
        #creating an empty list to receive the values
        values = []
        #checking which of the neighbourhood values is closer to the average
        for j in range(0, len(the_hood)):
            
            #getting the neighbourhood values
            values.append(new_data[the_hood[j]])
        
        #Selecting and replacing the value that strongly deviates for the
        #neighbour with the closest value to the mean      
        new_data[y,x] = min(values, key=lambda x:abs(mean-x)) 
    
    return(new_data)
    
    


#teste = filtro_neighbour(vel4vm[3],10)
