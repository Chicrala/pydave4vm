#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code creates the database to hold the information about the Poynting flux 
and morphological evolution of Active Regions(ARs) and the X-Ray flares 
associated with them. Data ranging from 2012-2018 will be used to conduct this 
analysis.

The information displayed in the Morphology and Events tables can be downloaded
in the Space Weather Prediction Center (SWPC): https://www.swpc.noaa.gov/

To conduct the plasma velocity estimation the three magnetic field components 
downloaded from the Spaceweather HMI Active Region Patch (SHARP) are used.
The data series used is the hmi.sharp_cea_720s which is the definitive data 
wherein the vector B has been remapped to a Lambert Cylindrical Equal-Area 
projection and decomposed into B_radial, B_phi, and B_theta.

Plasma velocities are estimated using a Python version of DAVE4VM:
https://github.com/Chicrala/pydave4vm
Which is a translation of the original code published by Dr. Schuck written in
IDL. The original code can be downloaded at:
https://ccmc.gsfc.nasa.gov/lwsrepository/DAVE4VM_description.php

Combining the velocity and magnetic field the Poynting flux is them calculated.
The integrated magnetic (vertical) and energy fluxes over the whole image space
and also along the Polarity Inversion Lines (PILs) is also calculated and 
stored as a product.

More information about the SHARPs can be found at:
http://jsoc.stanford.edu/doc/data/hmi/sharp/sharp.htm

In this version only the spatially integrated quantities are maintained saving
space in the database itself.

@author: andrechicrala
https://github.com/Chicrala
"""

# To create the tables we need these packages.
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import sqlalchemy.types as types
import json

# Creating the Base Object for the tables.
Base = declarative_base()

# Defining a class to hold the active region table.
class ActiveRegion(Base):
    '''
    ===========================================================================
    This table have the identification for each set of Observations  that are 
    derived from Active Regions (ARs) SHARP data. The names of each row will be 
    described below along with the keywords to call them. Note that the names
    of each row are case sensitive.
    ===========================================================================
    Keywords:
    =========
    id: The Primary Key (PK) and unique identifier of each column of this 
    table. It is used as a Foreign Key (FK) for the Observations, Morphology 
    and Events tables.
    
    harp_number: The HMI Active Region Patches (HARP) number associated with 
    the set of products that were used to derive the products for an AR.
    
    noaa_number: The AR National Oceanic and Atmospheric Administration(NOAA) 
    number assigned to the active region that is being observed by a HARP
    series.
    
    noaa_number2, noaa_number3: if the HARP observation window includes more 
    than one AR the NOAA numbers of the other regions will be stored in this
    entries.
    
    columnshape: column to hold the vertical shape of the image this is 
    necessary to re-assemble the numpy array that are stored as strings.
    ===========================================================================
    '''
    # Defining the tablename.
    __tablename__='activeregion'
    
    # The ID column which will be the PK for this table and FK for the other 
    # tables.
    AR_id=sql.Column('aridpk', sql.Integer, primary_key=True)
    
    # Defining the columns to hold the identifiers for the noaa and harp 
    # numbers columns.
    harp_number=sql.Column('harpnumber', sql.Integer, nullable=False)
    noaa_number1=sql.Column('noaanumber1', sql.Integer, nullable=True)
    noaa_number2=sql.Column('noaanumber2', sql.Integer, nullable=True)
    noaa_number3=sql.Column('noaanumber3', sql.Integer, nullable=True)
    
    # Creating a column to store the maximum Hale classification of each
    # individual AR in this table.
    max_hale_class1=sql.Column('maxhaleclass1', sql.String, nullable=True)
    max_hale_class2=sql.Column('maxhaleclass2', sql.String, nullable=True)
    max_hale_class3=sql.Column('maxhaleclass3', sql.String, nullable=True)
    
    # Defining a column to hold the vertical shape of the image this is 
    # necessary to re-assemble the numpy array that are stored as strings.
    columnshape=sql.Column('columnshape', sql.Integer, nullable=False)
    rowshape=sql.Column('rowshape', sql.Integer, nullable=False)
    
    # Defining the relationships between the tables.
    obs=relationship('Observations')
    morp=relationship('Morphology')
    eve=relationship('Events')

class Observations(Base):
    '''
    ===========================================================================
    This table holds the products derived from the HMI magnetic field 
    observations which are the veloticity and Poynting flux components. The 
    names of each row will be described below along with the keywords to call 
    them. Note that the names of each row are case sensitive.
    ===========================================================================
    Keywords:
    =========
    id: The Primary Key (PK) and unique identifier of each column of this 
    table.
    
    ar_id: The Foreign Key (FK) that stablishes the connection between this 
    table and the ActiveRegion table.
    
    timestamp: The column with the timestamp of this observation pair. This 
    column take the 2nd observation time stamp.
    
    poyn_Sn, poyn_St, Poyn_Ss: these columns store the Normal (Sn), Tangential 
    (St) and Total (Ss) pixel integrated Poynting flux components obtained 
    from the mean magnetic field and velocity components.
    
    int_Sn, int_St, int_Ss:these columns store the Normal (Sn), Tangential 
    (St) and Total (Ss) Poynting flux components integrated over the image
    space.
    
    int_PIL_Sn, int_PIL_pos_Sn, int_PIL_neg_Sn, int_PIL_St, int_PIL_pos_St,
    int_PIL_neg_st, int_PIL_Ss, int_PIL_pos_Ss, int_PIL_neg_Ss, int_PIL_Bx,
    int_PIL_By, int_PIL_Bz:these columns store the Normal (Sn), Tangential 
    (St) and Total (Ss) Poynting flux components posive, negative and net 
    contributions and the magnetic field components (Bx, By, Bz) integrated 
    over the image space around a Polarity Inversion Line (PIL).
    ===========================================================================
    '''
    
    # Declaring the tablename.
    __tablename__='observations'
    
    # Defining the PK column.
    OBS_id=sql.Column('obsidpk',sql.Integer, primary_key=True)
    
    # Defining a FK column to stabilishes the connection between this table
    # and the ActiveRegion table.
    ar_id=sql.Column('aridfk',sql.Integer, sql.ForeignKey(ActiveRegion.AR_id))
    
    # Defining the columns to hold the identifiers for the noaa numbers 
    # that represents the ARs being observed in this dataset.
    noaa_number1=sql.Column('noaanumber1',sql.Integer, nullable=True)
    noaa_number2=sql.Column('noaanumber2',sql.Integer, nullable=True)
    noaa_number3=sql.Column('noaanumber3',sql.Integer, nullable=True)
    
    # The column with the timestamp of this observation pair.
    # This column take the 2nd observation time stamp.
    timestamp_dt=sql.Column('timestampdt',sql.DateTime, nullable=False)
    timestamp_int=sql.Column('timestampint',sql.Integer, nullable=False)
    
    # This column keeps track of the time interval in seconds used into the 
    # calculations.
    deltat=sql.Column('deltat',sql.Float, nullable=False)
    
    # Defining the columns to store the integral of each Poynting flux
    # component over the image space.
    int_Sn=sql.Column('intsn',sql.Float, nullable=False)
    int_St=sql.Column('intst',sql.Float, nullable=False)
    int_Ss=sql.Column('intss',sql.Float, nullable=False)

    int_Sn_filt=sql.Column('intsnfilt',sql.Float, nullable=True)
    int_St_filt=sql.Column('intstfilt',sql.Float, nullable=True)
    int_Ss_filt=sql.Column('intssfilt',sql.Float, nullable=True)
    
    # Defining the columns to store the integral of each Poynting flux
    # and magnetic field component as well as their positive and negative 
    # contributions along the Polarity Inversion Lines.
    int_PIL_Sn=sql.Column('intpilsn',sql.Float, nullable=True)
    int_PIL_pos_Sn=sql.Column('intpilpossn',sql.Float, nullable=True)
    int_PIL_neg_Sn=sql.Column('intpilnegsn',sql.Float, nullable=True)
    
    int_PIL_St=sql.Column('intpilst',sql.Float, nullable=True)
    int_PIL_pos_St=sql.Column('intpilposst',sql.Float, nullable=True)
    int_PIL_neg_St=sql.Column('intpilnegst',sql.Float, nullable=True)
    
    int_PIL_Ss=sql.Column('intpilss',sql.Float, nullable=True)
    int_PIL_pos_Ss=sql.Column('intpilposss',sql.Float, nullable=True)
    int_PIL_neg_Ss=sql.Column('intpilnegss',sql.Float, nullable=True)

    int_PIL_Sn_filt=sql.Column('intpilsnfilt',sql.Float, nullable=True)
    int_PIL_pos_Sn_filt=sql.Column('intpilpossnfilt',sql.Float, nullable=True)
    int_PIL_neg_Sn_filt=sql.Column('intpilnegsnfilt',sql.Float, nullable=True)
    
    int_PIL_St_filt=sql.Column('intpilstfilt',sql.Float, nullable=True)
    int_PIL_pos_St_filt=sql.Column('intpilposstfilt',sql.Float, nullable=True)
    int_PIL_neg_St_filt=sql.Column('intpilnegstfilt',sql.Float, nullable=True)
    
    int_PIL_Ss_filt=sql.Column('intpilssfilt',sql.Float, nullable=True)
    int_PIL_pos_Ss_filt=sql.Column('intpilposssfilt',sql.Float, nullable=True)
    int_PIL_neg_Ss_filt=sql.Column('intpilnegssfilt',sql.Float, nullable=True)
    
    # Schrijver's R.
    logR=sql.Column('logr',sql.Float, nullable=True)
    logR_filt=sql.Column('logrfilt',sql.Float, nullable=True)
    
    # Creating a column to store the sharp metadata as a json object.
    hmi_meta_data=sql.Column('hmimetadata', sql.JSON, nullable=False)
    
    # Stabilishing the relationship between this table and the ARs table.
    ars=relationship('ActiveRegion', backref=backref('observations', order_by=ar_id))
   
class Morphology(Base):
    '''
    ===========================================================================
    This table holds the information found on the Solar Region Summary (SRS)
    files produced by SWPC. Below the quantities stored in this column will be
    described with and each row name will be also mentioned. Note that row and
    column names are case sensitive. When they differ from how they are named
    in the original files the original column name which the data was extracted
    will be placed in brackets.
    ===========================================================================
    Keywords:
    =========
    morp_id: has the Morfologia table id of a set of entries. This is the
    Primary Key of this table.
    
    ar_id: has the Foreign Key that connects the tables Morfologia and ARs.
    
    daystamp: stores the date which the properties written in this column were 
    derived.
    
    noaa_number: An SESC region number assigned to a sunspot group during its 
    disk passage. Note: The Solar Region Number reached 10,000 in 
	July 2002. However, SWPC products continue to use 4-digit region 
	numbers, with leading zeros.

    latitude, longitude (Location): Sunspot group location, in heliographic 
    degrees latitude and degrees east or west from central meridian, rotated 
    to 2400 UTC. Considering the solar disk up and left are the positive
    directions for latitude and longitude respectivelly.
    
    Lo: Carrington longitude of the group.
    
    area: Total corrected area of the group in millionths of the solar 
    hemisphere.
    
    mcintosh (Z): Modified Zurich classification of the group.
    
    LL: Longitudinal extent of the group in heliographic degrees.
    
    NN: Total number of visible sunspots in the group.
    
    Mag Type (hale): Magnetic classification of the group.
    ===========================================================================
    More information about the text files that are being mined to produce
    this table can be found at:
        
    ftp://ftp.swpc.noaa.gov/pub/forecasts/SRS/README
    
    The complete archive can be acessed at:
        
    ftp://ftp.swpc.noaa.gov/pub/warehouse
    ===========================================================================
    '''
    
    # Declaring the tablename.
    __tablename__='morphology'
    
    # Defining the columns.
    # Starting by the ID column which is the Primary Key of this table.
    MORP_id=sql.Column('morphidpk',sql.Integer, primary_key=True)
    
    # Defining the Foreign Key column.
    ar_id=sql.Column('aridfk',sql.Integer, sql.ForeignKey(ActiveRegion.AR_id))
    
    # The columns with SWPC - SRS mined data.
    noaa_number=sql.Column('noaanumber',sql.Integer, nullable=True)
    mcintosh=sql.Column('mcintosh',sql.String, nullable=True)
    hale=sql.Column('hale',sql.String, nullable=True)
    daystamp_dt=sql.Column('daystampdt',sql.DateTime, nullable=True)
    daystamp_int=sql.Column('daystampint',sql.Integer, nullable=True)
    latitude=sql.Column('latitude',sql.Integer, nullable=True)
    longitude=sql.Column('longitude',sql.Integer, nullable=True)
    LL=sql.Column('ll',sql.Integer, nullable=True)
    Lo=sql.Column('lo',sql.Integer, nullable=True)
    NN=sql.Column('nn',sql.Integer, nullable=True)
    area=sql.Column('area',sql.Integer, nullable=True)
    
    # Stabilishing the relationship between this table and the ARs table.
    ars=relationship('ActiveRegion', backref=backref('morphology', order_by=ar_id))  


class Events(Base):
    '''
    ===========================================================================
    This table holds the information found on the Events files produced by 
    SWPC. Below the quantities stored in this column will be described with 
    and each row name will be also mentioned. Note that row and column names 
    are case sensitive. When they differ from how they are named in the 
    original files the original column name which the data was extracted
    will be placed in brackets.
    ===========================================================================
    Keywords:
    =========
    eve_id: Eventos Primary Key for a set of an event.
    
    ar_id: has the Foreign Key that connects the tables Eventos and ARs.
    
    flareclass (Particulars): Additional information from the report, chosen 
    on the basis of the report type.
    
    event_begin, event_max, event_end (Begin, Max, End):
    The UTC Time (Coordinate Universal Time, same as UT) of the beginning, 
    maximum, and end of the event as reported by the observing site. 
    "////" indicates a missing time. 
    The UTC day of the event's begin time is the UTC day of the list. 
    The UTC day of the maximum and/or end times may or may not be the same 
    as the begin time. Most solar events are several hours in duration. If 
    the maximum or end time is less than the begin time, then assume the 
    times are for the next UTC day. A single letter can proceed a Begin, Max, 
    or End time. A=after, B=before, U=uncertain. For example the begin time 
    A0146 means the event began after 0146.These dates are saved in both 
    Integer and datetime formats.
    

    The begin time of an x-ray event is defined as the first minute, in a 
    sequence of 4 minutes, of steep monotonic increase in 0.1-0.8 nm flux. 
    The x-ray event maximum is taken as the minute of the peak x-ray flux. 
    The end time is the time when the flux level decays to a point halfway 
    between the maximum flux and the pre-flare background level. 

    The begin time of an SXI flare (XFL) is minutes following the associated
    x-ray event. The maximum time is the most intense period in the brightest 
    region of the SXI image. The end time is the last SXI image before the X-ray
    event end time. 
    
    noaa_number (Reg#): The SWPC-assigned solar region number with a 1
    preceding it.
    
    event_number (Event): This is an arbitrary event number assigned by SWPC. 
    It groups several reports into a single event, as determined by the SWPC 
    forecaster.
    ===========================================================================
    More information about the text files that are being mined to produce
    this table can be found at:
        
    ftp://ftp.swpc.noaa.gov/pub/indices/events/README
    
    The complete archive can be acessed at:
        
    ftp://ftp.swpc.noaa.gov/pub/warehouse
    ===========================================================================
    '''
    # Declaring the table name.
    __tablename__='eventos'
    
    # Defining the columns.
    # Starting by the Primary Key (ID) column.
    EVE_id=sql.Column('eveidpk',sql.Integer, primary_key=True)
    
    # Defining the Foreign Key column.
    ar_id=sql.Column('aridfk',sql.Integer, sql.ForeignKey(ActiveRegion.AR_id))
    
    # Defining the columns to store the events data.
    flareclass=sql.Column('flareclass',sql.String, nullable=True)
    
    event_begin_dt=sql.Column('eventbegindt',sql.DateTime, nullable=True)
    event_max_dt=sql.Column('eventmaxdt',sql.DateTime, nullable=True)
    event_end_dt=sql.Column('eventenddt',sql.DateTime, nullable=True)
    
    event_begin_int=sql.Column('eventbeginint',sql.Integer, nullable=True)
    event_max_int=sql.Column('eventmaxint',sql.Integer, nullable=True)
    event_end_int=sql.Column('eventendint',sql.Integer, nullable=True)
    
    noaa_number=sql.Column('noaanumber',sql.Integer, nullable=True)
    event_number=sql.Column('eventnumber',sql.Integer, nullable=True)
    
    daystamp_dt=sql.Column('daystampdt',sql.DateTime, nullable=True)
    daystamp_int=sql.Column('daystampint',sql.Integer, nullable=True)
    
    # Stabilishing the relationship between the Eventos and the ARs tables.
    ars=relationship('ActiveRegion', backref=backref('events', order_by=ar_id))

if __name__ == '__main__':
    # Create an engine that stores data in the local directory.
    engine=create_engine('sqlite:///main.db')    

    # Create all tables in the engine.
    # This is equivalent to "Create Table" statements in raw SQL.
    Base.metadata.create_all(engine)
