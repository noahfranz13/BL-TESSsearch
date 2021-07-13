# Combined pipeline to simplify analysis of turboSETI files
# Uses both find_event_pipeline and plot_event_pipeline turboSETI methods
# to create waterfall plots of the events found in a full cadence 

def FindPlotEvents(dataDir, threshold=3):
    '''
    dataDir : string with directory housing both the .dat and .h5 files

    returns : waterfall plots of data
    '''

    import os, glob
    from turbo_seti.find_event.find_event_pipeline import find_event_pipeline
    from turbo_seti.find_event.plot_event_pipeline import plot_event_pipeline
    #%matplotlib inline

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
    plot_event_pipeline(csvPath, h5listPath, filter_spec=f'{threshold}', user_validation=True)
