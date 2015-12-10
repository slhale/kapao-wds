
# import the python3 print function
from __future__ import print_function

#imports
import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import matplotlib.colors as c
import astropy
from astropy.io import ascii
from StringIO import StringIO
from matplotlib.colors import LogNorm
import pylab
from matplotlib.ticker import NullFormatter
import numpy.ma as ma
np.set_printoptions(threshold='nan')
import pickle
from collections import Counter 
from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.cm as cm
#imports added by Sarah
from astropy.time import Time
import re

def formatWds(wds):
    '''
        Converts the combined RADec column of the WDS master table to 
        two separate columns of RA and Dec. 
        Takes the WDS table and returns a modified version of it. 
    '''
    
    radec = wds['col21']# TODO later set this to radec col
    
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
    
    # Add the new lists as two new columns to the wds table
    raCol = astropy.table.Column(data=ra, name='RA')
    decCol = astropy.table.Column(data=dec, name='Dec')
    wds.add_column(raCol)
    wds.add_column(decCol)
    
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


def getSmallerWdsInterestingHereString():
    '''
        Gets a string of the  WDS table constrained to what stars 
        are both interesting and viewable. Returns only the columns with 
        specified names. (Those are assumed to be the columns of
        interest.) 
    '''
    global wdsInterestingHere
    
    # Not including numObjs because it doesn't seem to have much in it
    return str(wdsInterestingHere[discovererAndNumber,  posAngleFirst, posAngleLast, 
                                    sepFirst, sepLast, priMag, secMag, spectralType, 
                                    priRaProperMotion, priDecProperMotion, raCoors, decCoors])


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


# TODO This doesn't work yet
def calcSiderealTime(longitude=-117, time=Time.now()):
    '''
        Calculate the sidereal time for a specific time and place. 
        By default calculates for the current time at longitude -117.
        
        This function cannot work until 
        https://github.com/astropy/astropy/issues/3275
        has been resolved. 
    ''' 
    
    # Sidereal time on Nov 26, 2015 at 0-oclock is 4:16:00 ish 

    # Set the time and place
    #nowtime = Time.now()
    #longitude = -117
    # Get the corresponding sidereal time
#    siderealTime = nowtime.sidereal_time('apparent', longitude)
    
    startTime = Time('2015-11-26 00:00:00', scale='utc')
    startSidereal = 041600.0 #'04:16:00'
    
    # If the sidereal time we are trying to calculate is after this, then we can 
    # calculate it by adjusting the sidereal time by 4 minutes for each day after
    elapsedDays = time - startTime # float of days 
    adjustment = float(str(elapsedDays)) * 4 # in minutes
    #print(elapsedDays)
    #print(float(str(elapsedDays)))
    # if the adjustment is greater than 60, then we need to account for this when 
    # converting into hhmmss
    hours = 0
    mins = adjustment
    while adjustment >= 60:
        mins = mins - 60
        hours = hours + 1
        
    sidereal = startSidereal + mins*100 + hours*10000
    #print(mins)
    #print(hours)
    #print(sidereal)
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
    

# TODO replace sidereal adjustment parameter with an actual calculation for it 
# Depends on the sidereal time github issue being fixed

# The default inputs are currently specific to the 2015 Oct 15 observation date 
# On this date the sidereal time will be about 1.6 h ahead of earth time
# Uses the global constrain var to determine how the wds table is constrained
def setTimeConstraints(startHA=190000.0, stopHA=240000.0, siderealAdjust=13000.0):
    '''
        Set the upper and lower bounds for the constraints which 
        are relevant to viewing time. (Does not constrain the wds list.)
        Takes floats for startHA, stopHA, and siderealAdjust. 
    '''
    global constraints
    
    startRA = startHA + siderealAdjust
    stopRA = stopHA + siderealAdjust
    
    # Account for the 24 hour clock, and roll over if we pass midnight on either
    if startRA > 240000.0:
        startRA = startRA - 240000.0
    if stopRA > 240000.0:
        stopRA = stopRA - 240000.0
    
    # the stop time is the "upper bound", so it's first in the tuple
    constraints['ra'] = (stopRA, startRA)
    
    
def constrain():
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
    
    # Reset what wdsInteresting and wdsInterestingHere are so that we 
    # can get stars which we previously constrained out 
    wdsInteresting = wdsMaster
    wdsInterestingHere = wdsMaster
    
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
    limits['dec'] = (wdsInteresting[decCoors] > (340000.0 - 350000.0)) & (wdsInteresting[decCoors] < (340000.0 + 350000.0))
    
    # Combine all the limits together to get the full limits
    generalLimits = limits['separation'] & limits['magnitude'] & limits['delta magnitude']
    hereLimits = limits['separation'] & limits['magnitude'] & limits['delta magnitude'] & limits['dec'] & limits['ra']
    
    # Apply the limits to the catalog
    wdsInteresting = wdsInteresting[np.argwhere(generalLimits)]
    wdsInterestingHere = wdsInterestingHere[np.argwhere(hereLimits)]
    

def write(filename='object_list.txt'):
    '''
        Writes the contents of wdsInteresting to a file. 
        The default filename is object_list.txt
    '''
    global wdsInteresting
    
    log = open(filename, "w")
    print(wdsInteresting, file = log)

## TODO  Document these functions
## TODO Add key with constraints and total number 
## TODO Color the plots in accordances with the constraints 
def plotStars(catalog):
    #simple RA and DEC plot without conversion to decimal
    x = np.ravel(catalog[raCoors])
    y = np.ravel(catalog[decCoors])
    
    ### TODO 'color' code this plot with magnitude as size of point
    ### TODO color code this plot with separation as color  
    ### TODO 'color' code this plot with delta mag as shape   
    
    plt.hist2d(x, y, bins = 100, norm=LogNorm())
    plt.xlim(xmin = 240000.00, xmax=0.00)
    plt.ylim(ymin = -900000.0, ymax=900000.0)
    plt.gca().invert_xaxis()
    plt.title('WDS Histogram of RA vs. DEC (100 bins)')
    plt.xlabel('RA hhmmss')
    plt.ylabel('DEC ddmmss')
    plt.savefig('RA_DEC_histogram_extracted.png', format='png',dpi=1000)

def plotMagSep(catalog):
    #plot of magnitude vs separation for KAPAO constrains
    x = np.ravel(catalog[sepFirst])
    y = np.ravel(catalog[priMag])

    plt.hist2d(x, y, bins = 100, norm=LogNorm())
    plt.xlim(xmin = 2.00, xmax=0.00)
    plt.ylim(ymin = 2.00, ymax=9.00)
    plt.gca().invert_xaxis()
    plt.title('KAPAO-limited Separation vs. Magnitude (100 bins)')
    plt.xlabel('Separation')
    plt.ylabel('Magnitude')
    plt.savefig('Sep_v_Mag_extracted.png', format='png',dpi=1000)

#print(wdsMaster)
#setTimeConstraints()
#setStarConstraints()
#constrain()
#print(wdsInteresting)
#print(wdsInterestingHere)
##write()
calcSiderealTime()

