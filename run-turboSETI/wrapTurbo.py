# Imports
import os, sys, time
import numpy as np
import pandas as pd
from turbo_seti.find_doppler.find_doppler import FindDoppler

def wrap_turboSETI(iis, infilename, outDir, t=True):
    '''
    iis : numpy array of indexes to run through
    infilename : csv filename of filepaths and if it has run through turboSETI
    outDir : directory to store output subdirectories
    t : boolean, if true runtime is written to spreadsheet

    returns : outputs .dat files from turboSETI
    '''

    # Make sure index list is an Array
    if type(iis) == str:
        if iis[0] == '[' or iis[-1] == ']':
            iis = np.fromstring(iis.strip('[]'), dtype=int, sep=',')
        else:
            print('Unexpected Format')
    elif type(iis) != type(np.array([])):
        iis = np.array(iis)

    # Read in spreadsheet for files not run through TurboSETI
    filepath = os.path.join(os.getcwd(), infilename)
    fileinfo = pd.read_csv(filepath)

    # Select necessary columns
    filepaths   = fileinfo['FILE PATH'].to_numpy()
    filenames   = fileinfo['FILE NAME'].to_numpy()
    target      = fileinfo['TARGET NAME'].to_numpy()
    tois        = fileinfo['TOI'].to_numpy()
    spliced     = fileinfo['SPLICED?'].to_numpy()

    # Run turboSETI
    for ii, infile in zip(iis, filepaths[iis]):

        # start timer
        if t:
            start = time.time()

        # Set up output subdirectory
        outdir = os.path.join(outDir, 'TOI-{}'.format(tois[ii]))

        # for now just
        print("it's working!!")

        # Uncomment to run turboSETI

        # # Make out directory if it doesn't exist
        # if not os.path.exists(outdir):
        #     os.makedirs(outdir)
        #
        # # Run turboSETI
        # fd = FindDoppler(infile, max_drift=4, snr=10, out_dir=outdir)
        # fd.search(n_partitions=32)
        #
        # # End timer and write to spreadsheet if time is true
         if t:
             runtime = time.time() - start
             print()
             print(f'{target[ii]} Runtime : {runtime}')
            #fileinfo.iloc[ii, 9] = runtime

        # # Write outfile path to dataframe
        # name = filenames[ii].split('.')[0] + '.dat'
        # fileinfo.iloc[ii, 10] = os.path.join(outdir, name)
        #
        # # Update spreadsheet to reflect turboSETI run
        # fileinfo.iloc[ii, 8] = 'TRUE'

    #fileinfo.to_csv(filepath, index=False)

    time.sleep(1)


def main():
    '''
    Access spreadsheet with file information data then run turboSETI on those
    files if it has not already been run. Outputs to subdirectories labelled by
    cadence ON target inside specified directory
    '''

    dir = '/datax/scratch/noahf/turboSETI-outFiles'
    infile = 'franz-turboSETI-input-file-info.csv'

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', help='csv of filepaths and if turboSETI', type=str, default=infile)
    parser.add_argument('--ii', help='Array of indexes to run through turboSETI')
    parser.add_argument('--outdir', help='output directory', type=str, default=dir)
    parser.add_argument('--timer', help='Should the runtime be recorded', type=bool, default=True)
    args = parser.parse_args()

    wrap_turboSETI(args.ii, args.infile, args.outdir, t=args.timer)

if __name__ == '__main__':
    sys.exit(main())
