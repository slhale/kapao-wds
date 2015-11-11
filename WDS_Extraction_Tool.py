
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

# Import the WDS catalog
#wdsMaster = astropy.io.ascii.read('WDS_CSV_cat_1-24_FIN2.txt', 
#                delimiter =',',guess=False, Reader =ascii.NoHeader,
#                fill_values=[('.', '-999'), ('', '-999')])
wdsMaster = astropy.io.ascii.read('WDS_CSV_cat_1-24_FIN2.txt', #'WDS_CSV_cat.txt', 
                delimiter =',',guess=False, Reader =ascii.NoHeader,
                fill_values=[('.', '-999'), ('', '-999')])
# Create the sub-catalog we want (to be narrowed down by constrain function)
wdsInteresting = wdsMaster
# Create sub-sub catalog which has the interesting stars that we can view
wdsInterestingHere = wdsInteresting

# Associate each row with its type
# e.g. Using wdsMaster[numObjs] is equiv to wdsMaster['col2']
#oldCols = """
discovererAndNumber = 'col1'
numObjs = 'col2'
posAngleFirst = 'col3'
posAngleLast = 'col4'
sepFirst = 'col5'
sepLast = 'col6'
priMag = 'col7'
secMag = 'col8'
spectralType = 'col9'
priRaProperMotion = 'col10'
priDecProperMotion = 'col11'
raCoors = 'col14'
decCoors = 'col15'
#"""
#####################################Implement use of other WDS later
newCols = """
discovererAndNumber = 'col2'
numObjs = 'col3'
posAngleFirst = 'col7'
posAngleLast = 'col8'
sepFirst = 'col9'
sepLast = 'col10'
priMag = 'col11'
secMag = 'col12'
spectralType = 'col13'
priRaProperMotion = 'col14'
priDecProperMotion = 'col15'
#raCoors = 'col20'## NOPE radec is on 21, need to parse to get each
#decCoors = 'col21'
radec = 'col21'
"""

# Constriant parameters
# constraints is the actual numbers, while limits has the boolean statements
constaints = {}
limits = {}

def getWdsInterestingHere():
    global wdsInterestingHere
    return wdsInterestingHere

def getWdsInteresting():
    global wdsInteresting
    return wdsInteresting

def getWdsMaster():
    global wdsMaster
    return wdsMaster

def calcDeltaMags():
    ''' Creates an array with the delta magnitudes of WDS objects '''
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
    ''' Calculate the sidereal time for a specific time and place. 
        By default calculates for the current time at longitude -117. ''' 
    
    return time.sidereal_time('apparent', longitude=-117)
    

# Sets the upper and lower bounds for constraining stars of the wds table
# does not actually apply the constraints
# takes tuples of upper and lower floats, in the format (upper, lower)
def setStarConstraints(separation=(2.0, 0.5), magnitude=(7.0, -10.0), deltaMag=(2.0, -2.0)):
    ''' Set the upper and lower bounds for the constraints.
        (Does not constrain the wds list.) '''
    global constaints
    
    constaints['separation'] = separation
    constaints['magnitude'] = magnitude
    constaints['delta magnitude'] = deltaMag

# Sets the upper and lower bounds for constraining stars of the wds table
# does not actually apply the constraints
# takes floats in format hhmmss for hour angle
# TODO replace sidereal adjustment parameter with an actual calculation for it 
def setTimeConstraints(startHA=190000.0, stopHA=240000.0, siderealAdjust=13000.0):
    ''' Set the upper and lower bounds for the constraints.
        (Does not constrain the wds list.) '''
    global constaints
    
    startRA = startHA + siderealAdjust
    stopRA = stopHA + siderealAdjust
    
    # Account for the 24 hour clock, and roll over if we pass midnight on either
    if startRA > 240000.0:
        startRA = startRA - 240000.0
    if stopRA > 240000.0:
        stopRA = stopRA - 240000.0
    
    # the stop time is the "upper bound", so it's first in the tuple
    constaints['ra'] = (stopRA, startRA)
    

# The default inputs are currently specific to the 2015 Oct 15 observation date 
# On this date the sidereal time will be about 1.6 h ahead of earth time
# Uses the global constrain var to determine how the wds table is constrained
def constrain():#viewStart=190000.0, viewEnd=20000.0, siderealAdjust=13000.0):
    ''' Limit wdsInteresting to only stars that match our criteria ''' 
    global wdsInteresting
    global wdsInterestingHere
    global constaints
    global limits
    
    # Make a bunch of limits for a bunch of different things
    #limits['separation'] = (wdsInteresting[sepFirst] > 0.5) & (wdsInteresting[sepFirst] < 2.0)
    limits['separation'] = (constaints['separation'][0] > wdsInteresting[sepFirst]) & (wdsInteresting[sepFirst] > constaints['separation'][1])
    
    # Currently trying to not be too restrictive on mag 
    # Would get considerably more if switched from 7.0 to 8.0 
    #limits['magnitude'] = (wdsInteresting[priMag] > -10.0) & (wdsInteresting[priMag] < 7.0)
    limits['magnitude'] = (constaints['magnitude'][0] > wdsInteresting[priMag]) & (wdsInteresting[priMag] > constaints['magnitude'][1])
    
    ## TODO Add color of stars as a thing
    6
    deltaMag = calcDeltaMags()
    #limits['delta magnitude'] = (deltaMag > -2.0) & (deltaMag < 2.0)
    limits['delta magnitude'] = (constaints['delta magnitude'][0] > deltaMag) & (deltaMag > constaints['delta magnitude'][1])
    
    # Limit the viewing to within 19 h to 2 h 
    #  i.e. viewing from 8pm to 10pm, looking back 1h and ahead 4h
    #limits['ra'] = (wdsInteresting[raCoors] > (viewStart + siderealAdjust)) | (wdsInteresting[raCoors] < (viewEnd + siderealAdjust))
    
    # Limit the viewing to times/HA/RA that are acceptable 
    # If the stop time is less than the start, we have crossed over the 
    # midnight mark and need to do weird calculations
    if constaints['ra'][0] < constaints['ra'][1]:
        limits['ra'] = (constaints['ra'][0] > wdsInteresting[raCoors]) | (wdsInteresting[raCoors] > constaints['ra'][1])
    else:
        limits['ra'] = (constaints['ra'][0] > wdsInteresting[raCoors]) & (wdsInteresting[raCoors] > constaints['ra'][1])
    
    
    # Limit the declination to within 3 h = 35 deg of overhead
    # Using JPL's latitude, 34.2 deg = 34 deg
    limits['dec'] = (wdsInteresting[decCoors] > (340000.0 - 350000.0)) & (wdsInteresting[decCoors] < (340000.0 + 350000.0))
    
    # Combine all the limits together to get the full constraints
    generalConstraints = limits['separation'] & limits['magnitude'] & limits['delta magnitude']
    hereConstraints = limits['separation'] & limits['magnitude'] & limits['delta magnitude'] & limits['dec'] & limits['ra']
    
    # Apply the constraints to the catalog
    wdsInteresting = wdsInteresting[np.argwhere(generalConstraints)]
    wdsInterestingHere = wdsInterestingHere[np.argwhere(hereConstraints)]
    
    # Testing adding rows 
    #wdsInterestingHere.add_row(['testing', 'TESTING', 'Test'])
#    print(len(wdsInterestingHere))
#    print(len(wdsInterestingHere[0]))
#    newRow = []
#    for i in range(0, len(wdsInterestingHere[0])):
#        newRow.append(i)
#    print(newRow)
#    wdsInterestingHere.insert_row(1,vals=newRow)
#    wdsInterestingHere.add_row(newRow)

#def inputConstrain():
#    startTime = float(raw_input("start time (earth) for viewing: "))
#    endTime = float(raw_input("end time (earth) for viewing: "))
#    lookBack = float(raw_input("how many hour anlges to look back when viewing: "))
#    lookAhead = float(raw_input("how many hour anlges to look forward when viewing: "))
#    siderealAdjust = float(raw_input("difference between sidereal and earth today?: "))
#    
#    constrain(startTime-lookBack, endTime+lookAhead, siderealAdjust)

def write(filename='object_list.txt'):
    ''' Writes the contents of wdsInteresting to a file. 
        The default filename is object_list.txt '''
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


setTimeConstraints()
setStarConstraints()
constrain()
#inputConstrain()
#print(wdsInteresting)
print(wdsInterestingHere)
#write()
#plotStars(wdsInteresting)
#plotMagSep(wdsInteresting)

