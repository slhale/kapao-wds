
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
wdsMaster = astropy.io.ascii.read('WDS_CSV_cat_1-24_FIN2.txt', 
                delimiter =',',guess=False, Reader =ascii.NoHeader,
                fill_values=[('.', '-999'), ('', '-999')])
# Create the sub-catalog we want (to be narrowed down by constrain function)
wdsInteresting = wdsMaster

# Associate each row with its type
# e.g. Using wdsMaster[numObjs] is equiv to wdsMaster['col2']
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

# Constriant parameters
constaints = {}

def printOriginal():
    ''' Prints the full wdsMaster catalog table to the console '''
    print(wdsMaster)

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

def calcSiderealTime(longitude=-117, time=Time.now()):
    ''' Calculate the sidereal time for a specific time and place. 
        By default calculates for the current time at longitude -117. ''' 
    
    return time.sidereal_time('apparent', longitude=-117)
    

def calcRaDecRestrictions():
    ''' Calculate what the range of RA and DEC that we want. '''
    
    # The hour angle range that we want is 19 h to 2 h 
    # The date we are assuming is October 15, 2015 
    # The location we are using is approximately that of JPL
    
def setConstraints():
    ''' Set the upper and lower bounds for the constraints.
        (Does not constrain the wds list.) '''
    global constaints
    
    constaints['separation'] = {};
    constaints['separation']['upper'] = 2.0
    constaints['separation']['lower'] = 0.5
    
    constaints['magnitude'] = {};
    constaints['magnitude']['upper'] = 7.0
    constaints['magnitude']['lower'] = -10.0
    
    constaints['delta magnitude'] = {};
    constaints['delta magnitude']['upper'] = 2.0
    constaints['delta magnitude']['lower'] = -2.0

def constrain():
    ''' Limit wdsInteresting to only stars that match our criteria ''' 
    global wdsInteresting
    
    # Make a bunch of limits for a bunch of different things
    limits = {}
    limits['separation'] = (wdsInteresting[sepFirst] > 0.5) \
                                & (wdsInteresting[sepFirst] < 2.0)
    # Currently trying to not be too restrictive on mag 
    # Would get considerably more if switched from 7.0 to 8.0 
    limits['magnitude'] = (wdsInteresting[priMag] > -10.0) \
                                & (wdsInteresting[priMag] < 7.0)
    deltaMag = calcDeltaMags()
    limits['delta magnitude'] = (deltaMag > -2.0) & (deltaMag < 2.0)
    # Limit the viewing to within 19 h to 2 h 
    #  i.e. viewing from 9pm to 11pm, looking back 1h and ahead 3h
    # This is specific to the 2015 Oct 22 observation date 
    # On this date the sidereal time will be about 1.8 h ahead of earth time
    limits['ra'] = (wdsInteresting[raCoors] > (200000.0 + 14800.0)) \
                        | (wdsInteresting[raCoors] < (20000.0 + 14800.0))
    # Limit the declination to within 3 h of overhead
    # Using JPL's latitude, 34.2 deg = 2.28 h = 2h 16' 48'' 
    limits['dec'] = (wdsInteresting[decCoors] > (21648.0 - 30000.0)) \
                        & (wdsInteresting[decCoors] < (21648.0 + 30000.0))
    
    # Combine all the limits together to get the full constraints
    constraints = limits['separation'] & limits['magnitude'] \
                    & limits['delta magnitude'] & limits['ra'] & limits['dec']
    
    # Apply the constraints to the catalog
    wdsInteresting = wdsInteresting[np.argwhere(constraints)]
    
    #print(limits['magnitude'])
    print(wdsInteresting)

def write(filename='object_list.txt'):
    ''' Writes the contents of wdsInteresting to a file. 
        The default filename is object_list.txt '''
    global wdsInteresting
    
    log = open(filename, "w")
    print(wdsInteresting, file = log)

constrain()
#write()

