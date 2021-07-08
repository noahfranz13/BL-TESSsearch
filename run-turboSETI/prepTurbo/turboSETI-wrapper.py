# Imports
import os, sys, time
import pandas as pd
import numpy as np
from turbo_seti.find_doppler.find_doppler import FindDoppler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def getSheet():
    '''
    gains access to the necessary google spreadsheet

    returns google spreadsheet client
    '''

    # Gain access to the google sheets and read in table with pandas
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    jsonfile = os.path.join(os.getcwd(), 'client_info.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonfile, scope)
    client = gspread.authorize(credentials)

    ss = client.open('franz-turboSETI-input-file-info').sheet1

    return ss


def readSpreadsheet():
    '''
    Reads in information from google sheets file-info table
    Necessary headers and example table here:
    https://docs.google.com/spreadsheets/d/1Jny2OhsXjr23HhlN_e5bJ-WITwP2HSFZJIBWg3Dpr_Y/edit?usp=sharing

    returns : pandas table for input into turboSETI wrapper
    '''

    # Read in info from spreadsheet
    ss = getSheet()
    ssdata = ss.get_all_records()
    fileinfo = pd.DataFrame.from_dict(ssdata)

    # Shorten fileinfo to only the ones that haven't run through turboSETI
    notDone = fileinfo[fileinfo['TurboSETI?'] == 'FALSE']

    return notDone

def writeSpreadsheet(row, column=9, msg='TRUE'):
    '''
    Updates google spreadsheet according to new changes

    row [int]    : row index that needs to be updated, count starts at 1
    column [int] : column index that needs to be updated, defaulted to 9,
                   count starts at 1
    msg [string] : Message to put in cell, defaulted to TRUE

    returns      : nothing, just updates the google sheet
    '''

    ss = getSheet()
    ss.update_cell(row, column, msg)

def wrap_turboSETI(outDir, t=True):
    '''
    outDir : directory to store output subdirectories
    t : boolean, if true runtime is written to spreadsheet

    returns : outputs .dat files from turboSETI
    '''

    # Read in spreadsheet for files not run through TurboSETI
    notdone = readSpreadsheet()

    # Select necessary columns
    filepaths   = notdone['FILE PATH'].to_numpy()
    filenames   = notdone['FILE NAME'].to_numpy()
    target      = notdone['TARGET NAME'].to_numpy()
    tois        = notdone['TOI'].to_numpy()
    spliced     = notdone['SPLICED?'].to_numpy()


    #isSpliced = np.where(spliced == 'spliced')[0]

    # Run turboSETI
    for ii, infile in enumerate(filepaths):

        # for now just run on spliced files
        if spliced[ii] == 'spliced':

            # start timer
            if t:
                start = time.time()

            # Set up output subdirectory
            outdir = os.path.join(outDir, f'TOI-{tois[ii]}')

            # Make out directory if it doesn't exist
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            # Run turboSETI
            fd = FindDoppler(infile, max_drift=4, snr=10, out_dir=outdir)
            fd.search(n_partitions=8)

            # for now just
            #print("it's working!!")

            # End timer and write to spreadsheet if time is true
            if t:
                runtime = time.time() - start
                print()
                print(f'{target[ii]} Runtime : {runtime}')
                writeSpreadsheet(ii+2, column=10, msg=runtime)

            # Write outfile path to spreadsheet
            name = filenames[ii].split('.')[0] + '.dat'
            writeSpreadsheet(ii+2, column=11, msg=os.path.join(outdir, name))

            # Update spreadsheet to reflect turboSETI run
            # Add 2 because sheets is 1 indexed (+1) and first line is a header (+1)
            writeSpreadsheet(ii+2)

def main():
    '''
    Access spreadsheet with file information data then run turboSETI on those
    files if it has not already been run. Outputs to subdirectories labelled by
    cadence ON target inside specified directory
    '''

    import argparse

    dir = '/datax/scratch/noahf/turboSETI-outFiles'

    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', help='turboSETI output directory', type=str, default=dir)
    parser.add_argument('--timer', help='should the run be timed', type=bool, default=True)
    args = parser.parse_args()

    if args.timer:
        wrap_turboSETI(args.outdir)
    else:
        wrap_turboSETI(args.outdir, t=False)

if __name__ == '__main__':
    sys.exit(main())
