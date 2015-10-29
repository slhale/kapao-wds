
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

# This is importing a "future" python version 3 print function.
from __future__ import print_function
%matplotlib


#import the WDS catalog
WDS_Master2 =astropy.io.ascii.read('WDS_CSV_cat_1-24_FIN2.txt', delimiter =',', guess=False, Reader =ascii.NoHeader, fill_values=[('.', '-999'), ('', '-999')])

#associate each row with its type
Discoverer_and_number = WDS_Master2['col1']
N_obs = WDS_Master2['col2']
Pos_angle_first = WDS_Master2['col3']
Pos_angle_last = WDS_Master2['col4']
Sep_first = WDS_Master2['col5']
Sep_last = WDS_Master2['col6']
Pri_mag = WDS_Master2['col7']
Sec_mag = WDS_Master2['col8']
Spectral_type = WDS_Master2['col9']
Pri_RA_prop_motion = WDS_Master2['col10']
Pri_DEC_prop_motion = WDS_Master2['col11']
RA_coords = WDS_Master2['col14']
DEC_coords = WDS_Master2['col15']

#magnitude difference
#calculating delta_mags for each object

Pri_mag_g = ma.filled(Pri_mag,[-999])
Sec_mag_g = ma.filled(Sec_mag,[-999])

Pri_mag_gg = np.asarray(Pri_mag_g, dtype = 'float_' )
Sec_mag_gg = np.asarray(Sec_mag_g, dtype = 'float_' )

Delta_mag = np.subtract(Pri_mag_gg, Sec_mag_gg)
Delta_mag_lim = Delta_mag[np.argwhere((Delta_mag<0.0) & (Delta_mag>-20.0) & (Sep_last>0.0) & (Sep_last <20.0))]

# Converting from (sexa?)decimal to degrees via Excel spreadsheet. 
RADEC_degrees =astropy.io.ascii.read('RADEC_indegrees.txt', delimiter =',', guess=False, Reader =ascii.NoHeader, fill_values=[('.', '-999'), ('', '-999')])
RA_degrees = RADEC_degrees['col1']
DEC_degrees = RADEC_degrees['col2']


### Default constraints:
Sep_max=2.0, Sep_min=1.0, Pri_mag_max=4.0, Pri_mag_min=3.0, Delta_mag_max=-1.0, Delta_mag_min=-2.0

#parameters
#This is where you can adjust parameters and cuttoff values for separation, magnitude, RA, DEC, and delta mag. Change the green!

# We want 1'' to 2'' separation
Sep_limits = (Sep_first>Sep_min) & (Sep_first <Sep_max)
# We want 3rd and 4th magnitude stars
Mag_limits = (Pri_mag>=Pri_mag_min) & (Pri_mag <=Pri_mag_max)

RA_lim1 = (RA_coords>140000.00) & (RA_coords <240000.00)
RA_lim2 = (RA_coords<20000.00) & (RA_coords >0000.00)
#RA_limits = (RA_coords>143000.00) || (RA_coords<20000.00)
#RA_lims = RA_coords.any(RA_coords>140000, RA_coords<20000)
DEC_limits = (DEC_coords>100000.0) & (DEC_coords<600000.0)

Mag_limits_0_3 = (Pri_mag>0.0) & (Pri_mag <=3.0)
Mag_limits_3_6 = (Pri_mag>3.0) & (Pri_mag <=6.0)
Mag_limits_6_9 = (Pri_mag>6.0) & (Pri_mag <=9.0)

# We want within +- 2.0 mag
Delta_limits = (Delta_mag<Delta_mag_max) & (Delta_mag>=Delta_mag_min)
Delta_mag_limits_sm = (Delta_mag<0.0) & (Delta_mag>=-1.5)
Delta_mag_limits_lg = (Delta_mag<1.5) & (Delta_mag>=-20.0)


#This is where I'm combing limits just to make them easier to change. 

#RA & DEC limits 
RADEClimits = RA_lim2 & DEC_limits

#norm limits 
RADECseplimits = RADEClimits & Sep_limits

#full list
limits = RADECseplimits & Mag_limits & Delta_limits
limits1 = DEC_limits & Sep_limits & Mag_limits

#6 lists of limits
limits_mag1_Deltasm = Mag_limits_0_3 & Delta_mag_limits_sm & RADECseplimits
limits_mag2_Deltasm = Mag_limits_3_6 & Delta_mag_limits_sm & RADECseplimits
limits_mag3_Deltasm = Mag_limits_6_9 & Delta_mag_limits_sm & RADECseplimits
limits_mag1_Deltalg = Mag_limits_0_3 & Delta_mag_limits_lg & RADECseplimits
limits_mag2_Deltalg = Mag_limits_3_6 & Delta_mag_limits_lg & RADECseplimits
limits_mag3_Deltalg = Mag_limits_6_9 & Delta_mag_limits_lg & RADECseplimits

#custom limits
limits_mag1 = Mag_limits_0_3 & RADECseplimits

#constraints applied - Choose your limits variable from the kernel above! Mix and match!
constraints = limits

#lists from limits
#This now creates new lists for all of the objects within the cutoffs.
Discoverer_and_number_KAPAO = Discoverer_and_number[np.argwhere(constraints)]
Sep_first_KAPAO = Sep_first[np.argwhere(constraints)]
Sep_last_KAPAO = Sep_last[np.argwhere(constraints)]
Pri_mag_KAPAO = Pri_mag[np.argwhere(constraints)]
Sec_mag_KAPAO = Sec_mag[np.argwhere(constraints)]
Spectral_type_KAPAO = Spectral_type[np.argwhere(constraints)]
RA_coords_KAPAO = RA_coords[np.argwhere(constraints)]
DEC_coords_KAPAO = DEC_coords[np.argwhere(constraints)]


## Get the current time 
import datetime
now = datetime.datetime.utcnow()
now = now.strftime('%Y-%m-%d %H:%M:%S')
now = Time(now, format="iso", scale='utc')
#sunPos = astropy.coordinates.get_sun(nowtime)
#actually, we don't want the sun's position, we just need ours

