# Imports
import os
import pandas as pd
import numpy as np

import pymysql
import urllib
from barycorrpy import utc_tdb

from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord
from astropy import units as u

# tunable variables for later

numobs = 3 # Set minumum number of observations for a target to be recorded

# Get TESS Targets in GBT go_scans database
BLtargets = pymysql.connect(host=os.environ['BLIP'],user=os.environ['BLUSR'],
            password=os.environ['BLPASS'],database="BLtargets")

BLquery = """
SELECT *
FROM go_scans
WHERE target_name LIKE 'TIC%'
"""

go_scans = pd.read_sql(BLquery, BLtargets)

# Modify go_scans database for further calculations
go_scans['TIC ID'] = go_scans.target_name.apply(lambda v : int(v[3:]))
gbt = go_scans[['TIC ID', 'target_name', 'utc_observed', 'session']]


# Get full dataframe of TESS candidates
url = 'https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv'
toiPath = os.path.join(os.getcwd(), 'TESS-toi.csv')
urllib.request.urlretrieve(url, toiPath)
TESStoi = pd.read_csv(toiPath)

# Find TESS targets that transit during GBT observations

inTransitID = []
inTransitSession = []
gbtloc = EarthLocation.of_site('Green Bank Telescope')

for ticid in gbt['TIC ID'].unique():

    gbtInfo = gbt.loc[gbt['TIC ID'] == ticid]
    TESSinfo = TESStoi.loc[TESStoi['TIC ID'] == ticid]

    epoch = TESSinfo['Epoch (BJD)'].to_numpy()[0] # BJD
    period = TESSinfo['Period (days)'].to_numpy()[0]
    transitLength = TESSinfo['Duration (hours)'].to_numpy()[0]
    dist = TESSinfo['Stellar Distance (pc)'].to_numpy()[0]
    PMRA = float(TESSinfo['PM RA (mas/yr)'].to_numpy()[0])
    PMdec = float(TESSinfo['PM Dec (mas/yr)'].to_numpy()[0])

    ra = TESSinfo['RA'].to_numpy()[0]
    dec = TESSinfo['Dec'].to_numpy()[0]
    coords = SkyCoord(ra, dec, unit=(u.hourangle, u.deg), frame='icrs')

    obsTime = gbtInfo['utc_observed'].to_numpy()
    session = gbtInfo['session'].to_numpy()

    parallax = (1/dist) * 10**(-3) # units of mas

    # Convert Observed time to BJD
    tUTC = Time(obsTime, location=gbtloc)
    tbjd = utc_tdb.JDUTC_to_BJDTDB(tUTC, ra=float(coords.to_string().split()[0]),
                                       dec=float(coords.to_string().split()[1]),
                                       pmra=PMRA, pmdec=PMdec,
                                       px= parallax,
                                       obsname='Green Bank Telescope')[0]

    tbjd = tbjd[np.isfinite(tbjd)]

    # Does the GBT observation occur during a transit?
    if len(obsTime) >= numobs and period != 0: # Check for at least 3 obs

        tt = transitLength/24/2 # half transit time and convert to days

        # Create list of center transit times for each TIC ID

        for ii, obst in enumerate(tbjd):
            diff = np.abs(obst-epoch)
            numRot = int(np.ceil(diff/period))

            centerTransitTimes = []
            t = epoch
            for i in range(numRot):
                centerTransitTimes.append(t)
                if obst < epoch: # check if gbt obs happened before or after epoch
                    t-=period
                else:
                    t+=period

            # Since last value in transit time list is closest to observing time:
            epochf = centerTransitTimes[-1]
            startTransit = epochf - tt
            endTransit = epochf + tt

            if obst > startTransit and obst < endTransit:
                inTransitID.append(ticid)
                inTransitSession.append(session[ii])

# Extract go_scans info for transiting TESS Targets
outFrame = []

for tic, sess in zip(inTransitID, inTransitSession):

    mask = (go_scans['TIC ID'] == tic) & (go_scans['session'] == sess)

    if len(mask[mask==True]) >= numobs: # make sure target has 3 obs.
        outFrame.append(go_scans[mask])

targets = pd.concat(outFrame).drop_duplicates()

outFilePath = os.path.join(os.getcwd(), 'TESStargets.csv')

# Return csv file and number of unique TESS targets found transiting
targets.to_csv(outFilePath)
print(f'{len(targets.target_name.unique())} TESS targets found in transit')
