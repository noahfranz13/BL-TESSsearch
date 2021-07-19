# Combined pipeline to simplify analysis of turboSETI files
# Uses both find_event_pipeline and plot_event_pipeline turboSETI methods
# to create waterfall plots of the events found in a full cadence

def FindTransitTimes():
    '''
    Queries the TESS TOI webpage and go_scans database to get information
    on the transits of the ON TESS target to plot the start and end

    returns : list of transit times, first is the start and second is the end
    '''

    # Get full dataframe of TESS candidates
    url = 'https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv'
    toiPath = os.path.join(os.getcwd(), 'TESS-toi.csv')
    urllib.request.urlretrieve(url, toiPath)
    TESStoi = pd.read_csv(toiPath)

    # Get TESS Targets in GBT go_scans database
    BLtargets = pymysql.connect(host=os.environ['BLIP'],user=os.environ['BLUSR'],
                password=os.environ['BLPASS'],database="BLtargets")

    BLquery = """
    SELECT *
    FROM go_scans
    WHERE target_name LIKE 'TIC%'
    """

    go_scans = pd.read_sql(BLquery, BLtargets)

    # Get timing info on TESS target
    onTarget = sorted(glob.glob(dataDir + '/*.dat'))[0].split('.')[0].split('_')[-2]
    on_toi = np.where(TESStoi['TIC ID'].to_numpy() == onTarget[3:])[0]
    on_scans = np.where(go_scans['target_name'].to_numpy() == onTarget)[0]

    epoch = TESStoi['TRANSIT EPOCH (BJD)'].to_numpy()[on_toi]
    period = TESStoi['Period (days)'].to_numpy()[on_toi]
    tt = TESSinfo['Duration (hours)'].to_numpy()[on_toi]/24/2
    obst = go_scans['utc_observed'].to_numpy()[on_scans]

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
    transitTimes = [startTransit, endTransit]

    return transitTimes

def FindPlotEvents(dataDir, threshold=3, transitTimes=True):
    '''
    dataDir : string with directory housing both the .dat and .h5 files

    returns : waterfall plots of data
    '''

    import os, glob
    import urllib
    from turbo_seti.find_event.find_event_pipeline import find_event_pipeline
    #from turbo_seti.find_event.plot_event_pipeline import plot_event_pipeline
    #%matplotlib inline

    # Import local functions
    from noahf_plot_event_pipeline import plot_event_pipeline

    if transitTimes:
        transitTimes = FindTransitTimes()

    else:
        transitTimes = None

    # create .lst file for .h5 files
    h5list = sorted(glob.glob(dataDir + '/*.h5'))
    h5listPath = os.path.join(dataDir, 'h5-list.lst')

    with open(h5listPath, 'w') as L:
        for h5 in h5list:
            L.write(h5 + '\n')

    # create .lst file for .dat files
    datlist = sorted(glob.glob(dataDir + '/*.dat'))
    datlistPath = os.path.join(dataDir, 'dat-list.lst')

    with open(datlistPath, 'w') as L:
        for dat in datlist:
            L.write(dat+'\n')

    # run find_event_pipeline
    print('####################### Beginning Find Event Pipeline #######################')
    csvPath = os.path.join(dataDir, 'events-list.csv')
    find_event_pipeline(datlistPath, filter_threshold=threshold, number_in_cadence=len(datlist), csv_name=csvPath, saving=True);

    # run plot_event_pipeline
    print()
    print('####################### Beginning Plot Event Pipeline #######################')
    plot_event_pipeline(csvPath, h5listPath, filter_spec=f'{threshold}', user_validation=False, transit_times=transitTimes)
    #plot_event_pipeline(csvPath, h5listPath, filter_spec=f'{threshold}', user_validation=False)
