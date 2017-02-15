#!/usr/bin/env python

####################################
# File name: WDS_Extraction_Tool.py
# Author: Sarah Hale
# Email: shale@hmc.edu
# Date last modified: 2016-02-18
# Python Version: 2.7
####################################

# import the python3 print function
from __future__ import print_function

import numpy as np
from numpy import *
import astropy
from astropy.io import ascii
from StringIO import StringIO
import numpy.ma as ma
np.set_printoptions(threshold='nan')
from collections import Counter 
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import re
import json

# This funtion needs to be up here so it can be called during 'setup'
def formatWds(wds):
    '''
        Takes the WDS table and returns a modified version of it.
         - Converts the combined RADec column of the WDS master table to
           two separate columns of RA and Dec.
         - Creates a new column of delta mag from primary and secondary mags
    '''
    
    radec = wds['col21']
    primag = wds['col11']
    secmag = wds['col12']
    
    # Separate out RA and Dec from existing column and put into two lists
    ra = []
    dec = []
    split = ''
    # Loop over all the radec angles
    for i  in range(0, len(radec)):
        # Split the RA from the Dec
        # the ra appears before the dec, delimited by a + or -
        # if it's in the expected format, then the split should be
        #  [ra, + or -, dec]
        split = re.split('([+-])', radec[i])
        # If the split worked, add the ra and decs to new lists
        if len(split) == 3:
            ra.append(float(split[0]))
            dec.append(float(split[1]+split[2]))
        # Otherwise append blank values to the new lists to keep the lengths correct
        else:
            ra.append(-999999.9)
            dec.append(-999999.9)

    # Create list of delta mags from primary and secondary mags
    deltamag = []
    if len(primag) == len(secmag):
        for i  in range(0, len(primag)):
            # Take the difference such that it is positive
            # Assuming that secmag > primag
            if secmag[i] and primag[i]:
                delta = float(secmag[i]) - float(primag[i])
                # Round the output so the table doesn't get messed up
                delta = round(delta, 2)
                deltamag.append(delta)
            else:
                deltamag.append(-99.9)

    
    # Add the new lists as new columns to the wds table
    raCol = astropy.table.Column(data=ra, name='RA')
    decCol = astropy.table.Column(data=dec, name='Dec')
    deltaMagCol = astropy.table.Column(data=deltamag, name='DeltaMag')
    wds.add_column(raCol)
    wds.add_column(decCol)
    wds.add_column(deltaMagCol)
    
    return wds

# Import the WDS catalog
wdsMaster = astropy.io.ascii.read('WDS_CSV_cat.txt', 
                delimiter =',',guess=False, Reader =ascii.NoHeader,
                fill_values=[('.', '-999'), ('', '-999')])
wdsMaster = formatWds(wdsMaster)
# Create the sub-catalog we want (to be narrowed down by constrain function)
wdsInteresting = wdsMaster
# Create sub-sub catalog which has the interesting stars that we can view
wdsInterestingHere = wdsInteresting

# Associate each row with its type
# e.g. Using wdsMaster[numObjs] is equiv to wdsMaster['col2']

# Make this strings be variables so we can more easily change
# how the string names look without changing everything else
discovererAndNumber = 'Name'
numObjs = 'NumObjs'
posAngleFirst = 'PosAnglFrst'
posAngleLast = 'PosAnglLst'
sepFirst = 'SepFirst'
sepLast = 'SepLast'
priMag = 'PriMag'
secMag = 'SecMag'
spectralType = 'SpecType'
priRaProperMotion = 'PriRAPropMotion'
priDecProperMotion = 'PriDecPropMotion'
raCoors = 'RA'
decCoors = 'Dec'
deltaMag = 'DeltaMag'

## Rename all the columns to the useful names
wdsMaster['col2'].name = discovererAndNumber
wdsMaster['col3'].name = numObjs
wdsMaster['col7'].name = posAngleFirst
wdsMaster['col8'].name = posAngleLast
wdsMaster['col9'].name = sepFirst
wdsMaster['col10'].name = sepLast
wdsMaster['col11'].name = priMag
wdsMaster['col12'].name = secMag
wdsMaster['col13'].name = spectralType
wdsMaster['col14'].name = priRaProperMotion
wdsMaster['col15'].name = priDecProperMotion


# Constriant parameters
# Constraints is the actual numbers -- upper and lower bounds for
# different properties.
constraints = {}


def getWdsInterestingHere():
    '''
        Gets the WDS table constrained to what stars are both 
        interesting and viewable. 
    '''
    global wdsInterestingHere
    return wdsInterestingHere

def getWdsInteresting():
    '''
        Gets the WDS table constrained to what stars are interesting. 
    '''
    global wdsInteresting
    return wdsInteresting

def getWdsMaster():
    '''
        Gets the master WDS table. 
    '''
    global wdsMaster
    return wdsMaster

def hhmmssAdd(first, second):
    '''
        Function for adding hhmmss.s
        This is necissary because the number rolls over at 60, not 100.
    '''

    # Split up the two inputs into hh, mm, and ss
    ss1 = first % 100
    mm1 = (first % 10000 - first % 100) / 100
    hh1 = (first % 1000000 - first % 10000) / 10000
    ss2 = second % 100
    mm2 = (second % 10000 - second % 100) / 100
    hh2 = (second % 1000000 - second % 10000) / 10000

    # Add from least to most significant digits, taking care of rollover.
    ss = ss1 + ss2
    mm = mm1 + mm2
    hh = hh1 + hh2
    if ss > 60:
        mm = mm + 1
        ss = ss - 60
    if mm > 60:
        hh = hh + 1
        mm = mm - 60

    # Merge the hhmmss back together
    mm = mm * 100
    hh = hh * 10000
    return hh + mm + ss

def hhmmssSubtract(first, second):
    '''
        Function for subtracting hhmmss.s
        Second is subtracted from first, first - second.
        This is necissary because the number rolls over at 60, not 100.
    '''

    # Split up the two inputs into hh, mm, and ss
    ss1 = first % 100
    mm1 = (first % 10000 - first % 100) / 100
    hh1 = (first % 1000000 - first % 10000) / 10000
    ss2 = second % 100
    mm2 = (second % 10000 - second % 100) / 100
    hh2 = (second % 1000000 - second % 10000) / 10000

    # Subtract, taking care of rollover.
    ss = ss1 - ss2
    mm = mm1 - mm2
    hh = hh1 - hh2
    if ss < 0:
        mm = mm - 1
        ss = ss + 60
    if mm < 0:
        hh = hh - 1
        mm = mm + 60

    # Merge the hhmmss back together
    mm = mm * 100
    hh = hh * 10000
    return hh + mm + ss


def ddmmssToDeg(coordinate):
    # Check for + or - for Dec, and save so can add back later
    leadingSign = ''
    if '-' in str(coordinate):
        leadingSign = '-'
    elif '+' in str(coordinate):
        leadingSign = '+'

    data = float(coordinate)
    # Split the float into hh, mm, and ss
    # Casting all of the splits into int before string so there are no
    #  trailing decimal points
    #  Except seconds are rounded to 2 decimal points
    seconds = data % 100
    minutes = (data % 10000 - data % 100) / 100
    degrees = (data % 1000000 - data % 10000) / 10000

    # Divide through from mmss to decimal
    minutes = minutes / 60.0
    seconds = seconds / 3600.0
    degrees = float(leadingSign + str(degrees))
    
    degrees = degrees + minutes + seconds
    # TODO this isn't the best fix. Why are some of the lats out of range?
    if degrees < -90.0:
        degrees = -90.0
    elif degrees > 90.0:
        degrees = 90.0

    return degrees

def floatStringToColonSeparated(coordinate):
    # Check for + or - for Dec, and save so can add back later
    leadingSign = ''
    if '-' in coordinate:
        leadingSign = '-'
    elif '+' in coordinate:
        leadingSign = '+'

    data = float(coordinate)
    # Split the float into hh, mm, and ss
    # Casting all of the splits into int before string so there are no
    #  trailing decimal points
    #  Except seconds are rounded to 2 decimal points
    seconds = str(round(data % 100, 2))
    minutes = str(int((data % 10000 - data % 100) / 100))
    hours = str(int((data % 1000000 - data % 10000) / 10000))

    # Make sure there are leading zeros when one of them is <10
    if len(seconds.partition('.')[0]) < 2:
        seconds = '0' + seconds
    if len(minutes) < 2:
        minutes = '0' + minutes
    if len(hours) < 2:
        hours = '0' + hours

    # Concat them together with colons and return
    return leadingSign + hours + ':' + minutes + ':' + seconds

def tableToString(table, colWidth = 20, colonSeparated = True):
    '''
        Takes an astropy table and converts the table to a string.
        Also optionally takes the width of the column colWidth in 
        characters; the default value for this is 20.
        This is different from simply casting the table to a string 
        because it ensures that all of the columns are displayed. 
    '''
    
    # Number of rows in the table (excluding column names)
    rows = len(table.columns[1])
    # List of the names of each column 
    colNames = table.colnames
    
    # The string that will store the whole table
    string = ''
    
    # Keep track of the length of the last word so the column width
    # stays uniform
    lastWordLen = colWidth
    
    # Write the names of the columns to the string 
    for colName in colNames:
            string = string + (colWidth - lastWordLen)*' ' + str(colName)
            lastWordLen = len(colName)
    
    # Add a horizontal bar to separate the titles from the data a bit
    string = string + '\n' + len(string)*'-' + (colWidth - lastWordLen)*'-'
    
    # Loop over all of the elements of the table 
    for row in range(rows):
        lastWordLen = colWidth
        rowstring = ''
        # Write all the data in a row to a string 
        for colName in colNames:
            data = str(table[row][colName])
            # Remove the first and last characters from the string because 
            # they are just brackets 
            data = data[1:-1]
            # If this is RA or Dec want to convert from hhmmss.s to hh:mm:ss.s
            if colonSeparated and (colName == 'RA' or colName == 'Dec'):
                data = floatStringToColonSeparated(data)
            rowstring = rowstring + (colWidth - lastWordLen)*' ' + data
            lastWordLen = len(data)
        # Then add that string as a new line to the full table's string 
        string = string + '\n' + rowstring
    
    return string

# Added by shale 2017-01-30: Same default colWidth as tableToString, but changeable
def getSmallerWdsInterestingHereString(colWidth = 20, colonSeparated = True):
    '''
        Gets a string of the  WDS table constrained to what stars 
        are both interesting and viewable. Returns only the columns with 
        specified names. (Those are assumed to be the columns of
        interest.) 
    '''
    global wdsInterestingHere
    
    # Not including numObjs because it doesn't seem to have much in it
    # Shale 2017-02-06: Removing the position angles and proper motions.
    #                   Also reordering list.
    return tableToString(wdsInterestingHere[discovererAndNumber, raCoors, decCoors,
                                    priMag, deltaMag, sepFirst, sepLast, spectralType],
                                    colWidth, colonSeparated) # Added by shale on 2017-01-30


def calcDeltaMags():
    '''
        Creates an array with the delta magnitudes of WDS objects.
    '''
    # Calculating magnitude difference for each object
    # Make nice formats...
    Pri_mag_g = ma.filled(wdsInteresting[priMag],[-999])
    Sec_mag_g = ma.filled(wdsInteresting[secMag],[-999])
    Pri_mag_gg = np.asarray(Pri_mag_g, dtype = 'float_' )
    Sec_mag_gg = np.asarray(Sec_mag_g, dtype = 'float_' )
    # Then calculate the actual delta mags
    Delta_mag = np.subtract(Pri_mag_gg, Sec_mag_gg)
    
    return Delta_mag


def calcSiderealAdjustment(longitude=-117, time=Time.now()):
    '''
        Calculate the sidereal adjustmet time for a specific time and place. 
        By default calculates for the current time at longitude -117.
        The sidereal adjustment time is the difference between 
        the RA of a star and the HA of it on that day.  
        
        This function cannot fulll  work until 
        https://github.com/astropy/astropy/issues/3275
        has been resolved. 
        For now, the function approximates future sidereal
        times by adjusting by 4 minutes each day. 
    ''' 
    
    # Sidereal time on Nov 26, 2015 at 0-oclock is 4:16:00 ish 
    startTime = Time('2015-11-26 00:00:00', scale='utc')
    startSidereal = 041600.0 # hhmmss '04:16:00'
    
    # If the sidereal time we are trying to calculate is after this, then we can 
    # calculate it by adjusting the sidereal time by 4 minutes for each day after
    elapsedDays = time - startTime # float of days 
    adjustment = float(str(elapsedDays)) * 4 # in minutes
    
    # if the adjustment is greater than 24 h = 1440 min, then we need to 'wrap around'
    adjustment = adjustment % 1440

    # if the adjustment is greater than 60, then we need to account for this when 
    # converting into hhmmss
    hours = 0
    mins = adjustment
    while mins >= 60:
        mins = mins - 60
        hours = hours + 1
        
    sidereal = startSidereal + mins*100 + hours*10000
    
    return sidereal
    
def setStarConstraints(separation=(2.0, 0.5), magnitude=(7.0, -10.0), deltaMag=(2.0, -2.0)):
    '''
        Set the upper and lower bounds for the constraints which 
        are relevant to star properties. (Does not constrain the wds list.)
        Takes tuples in the format of and (upper, lower) pair of bounds. 
        The constraining properties are separation, magnitude, and deltaMag. 
    '''
    global constraints
    
    constraints['separation'] = separation
    constraints['magnitude'] = magnitude
    constraints['delta magnitude'] = deltaMag
    

def setTimeConstraints(startHA=190000.0, stopHA=240000.0, date=Time.now()):
    '''
        Set the upper and lower bounds for the constraints which 
        are relevant to viewing time. (Does not constrain the wds list.)
        Takes floats for startHA, stopHA. Takes an astropy Time object 
        for the date.  
    '''
    global constraints
    
    siderealAdjust = calcSiderealAdjustment(time = date) # TODO check github

    #startRA = startHA + siderealAdjust # TODO check math
    #stopRA = stopHA + siderealAdjust
    startRA = hhmmssAdd(startHA, siderealAdjust) # TODO check math
    stopRA = hhmmssAdd(stopHA, siderealAdjust)
    
    # Account for the 24 hour clock, and roll over if we pass midnight on either
    if startRA > 240000.0:
        startRA = startRA - 240000.0
    if stopRA > 240000.0:
        stopRA = stopRA - 240000.0
    
    # If the inputs are negative, also roll over those 
    if startRA < 0:
        startRA = 240000.0 + startRA
    if stopRA < 0:
        stopRA = 240000.0 + stopRA
    
    # the stop time is the "upper bound", so it's first in the tuple
    constraints['ra'] = (stopRA, startRA)
    
    
def setLocationConstraints(latitude=340000.0, viewWidth=350000.0):#northDec=(340000.0 + 350000.0), southDec=(340000.0 - 350000.0)):
    '''
        Set the upper and lower bounds for the constraints which 
        are relevant to viewing location. (Does not constrain the wds list.)
        Takes floats for laitude and viewWidth. Both are in deg:min:sec format. 
        The videWidth is how much +- you want to give to the laitude for stars.
    '''
    
    # Limit the declination to within 3 h = 35 deg of overhead
    # Using JPL's latitude, 34.2 deg = 34 deg
    northDec = latitude + viewWidth
    southDec = latitude - viewWidth

    # Check rollover for dec constraints
    if northDec > 900000:
        northDec = 900000
    if southDec < -900000:
        southDec = -900000
    
    # the north dec is the "upper bound", so it's first in the tuple
    constraints['dec'] = (northDec, southDec)


def addAirmassCol():
    '''
        Add a columns to the WDS table which is the calculated airmass for
        each object based off of its RA Dec and the location and time of
        the constrain.
    '''
    # Currently does NOT work! TODO
    # There is an astropy issue https://github.com/astropy/astropy/issues/5726
    # which will be fixed in astropy v1.3.1, but as of 2017-02-15 only
    # version 1.3(.0) has been released.
    
    secz = []
    # Loop over all the radec angles
    for i  in range(0, len(wdsInteresting[raCoors])):
        # Create a SkyCoord object from the RA and Dec
        #ra = floatStringToColonSeparated(wdsInteresting[raCoors][i])
        #dec = floatStringToColonSeparated(wdsInteresting[decCoors][i])
        ra = ddmmssToDeg(wdsInteresting[raCoors][i])
        dec = ddmmssToDeg(wdsInteresting[decCoors][i])
        starPos = SkyCoord(ra, dec, unit=(u.hour, u.deg))

        # Create an AltAz frame object
        preferences = {}
        with open('WDS_Preferences.json', 'r') as fp:
            preferences = json.load(fp)        
        observing_location = EarthLocation(lat=preferences['latitude'], lon=preferences['longitude'])
        aa = AltAz(location=observing_location)#, obstime=observing_time)
        
    
    # Add the list as new column to the wds table
    raCol = astropy.table.Column(data=ra, name='RA')
    wds.add_column(deltaMagCol)
    
    return wds


def constrain(airmass = False):
    '''
        Limits the WDS table to only stars that match our criteria.
        Creates wdsInteresting and wdsInterestingHere tables which 
        have constrained by star properties or by star properties and
        star location (in time).
        Does not modify wdsMaster.
        Has no returns, instead modifies the globals wdsInteresting 
        and wdsInterestingHere.
    ''' 
    global wdsMaster
    global wdsInteresting
    global wdsInterestingHere
    global constraints

    # Print what we are constraining with so it seems a bit responsive before
    # the long processing
    print("Constraining WDS with:")
    print(constraints)
    
    # Reset what wdsInteresting and wdsInterestingHere are so that we 
    # can get stars which we previously constrained out 
    wdsInteresting = wdsMaster
    wdsInterestingHere = wdsMaster

    # If we are told to do so, make an airmass column for the table
    #if airmass:
        #addAirmassCol()
    # TODO add this back in after associated astropy 1.3.1 has been released
    
    # Make a dictionary of limits (just for compactness).
    # Contains the boolean expressions with witch the wds table 
    # will be compared to. 
    limits = {}
    
    # Make a bunch of limits for a bunch of different things
    limits['separation'] = (constraints['separation'][0] > wdsInteresting[sepFirst]) & (wdsInteresting[sepFirst] > constraints['separation'][1])
    
    limits['magnitude'] = (constraints['magnitude'][0] > wdsInteresting[priMag]) & (wdsInteresting[priMag] > constraints['magnitude'][1])
    
    ## TODO Add color of stars as a thing
    
    deltaMag = calcDeltaMags()
    limits['delta magnitude'] = (constraints['delta magnitude'][0] > deltaMag) & (deltaMag > constraints['delta magnitude'][1])
    
    # Limit the viewing to times/HA/RA that are acceptable 
    # If the stop time is less than the start, we have crossed over the 
    # midnight mark and need to do weird calculations
    if constraints['ra'][0] < constraints['ra'][1]:
        limits['ra'] = (constraints['ra'][0] > wdsInteresting[raCoors]) | (wdsInteresting[raCoors] > constraints['ra'][1])
    else:
        limits['ra'] = (constraints['ra'][0] > wdsInteresting[raCoors]) & (wdsInteresting[raCoors] > constraints['ra'][1])
    
    
    # Limit the declination to within 3 h = 35 deg of overhead
    # Using JPL's latitude, 34.2 deg = 34 deg
    limits['dec'] = (constraints['dec'][0] > wdsInteresting[decCoors]) & (wdsInteresting[decCoors] > constraints['dec'][1])
    #limits['dec'] = (wdsInteresting[decCoors] > (340000.0 - 350000.0)) & (wdsInteresting[decCoors] < (340000.0 + 350000.0))
    
    # Combine all the limits together to get the full limits
    generalLimits = limits['separation'] & limits['magnitude'] & limits['delta magnitude']
    hereLimits = limits['separation'] & limits['magnitude'] & limits['delta magnitude'] & limits['dec'] & limits['ra']
    
    # Apply the limits to the catalog
    wdsInteresting = wdsInteresting[np.argwhere(generalLimits)]
    wdsInterestingHere = wdsInterestingHere[np.argwhere(hereLimits)]
    

def sortWdsInterestingHere(colName=raCoors):
    '''
        Sorts the wdsInterestingHere table based on a column.
        The default column to sort by is the RA coordinates. 
    '''
    global wdsInterestingHere
    
    print(wdsInterestingHere)
    print(colName)
    wdsInterestingHere.sort(colName)
    print(wdsInterestingHere)
    

def write(filename='object_list.txt'):
    '''
        Writes the contents of wdsInteresting to a file. 
        The default filename is object_list.txt
    '''
    global wdsInteresting
    
    log = open(filename, "w")
    print(wdsInteresting, file = log)


