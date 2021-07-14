# Imports
import os, sys, time
import numpy as np
import pandas as pd
import pymysql
from turbo_seti.find_doppler.find_doppler import FindDoppler

def wrap_turboSETI(iis, outDir, sqlTable, t=True, test=False):
    '''
    iis : numpy array of indexes to run through
    infilepath : csv file path of filepaths and if it has run through turboSETI
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

    # Read in mysql database
    db = pymysql.connect(host=os.environ['GCP_IP'], user=os.environ['GCP_USR'],
                        password=os.environ['GCP_PASS'], database='FileTracking')

    query = f'''
            SELECT *
            FROM {sqlTable}
            '''

    fileinfo = pd.read_sql(query, db)

    if test:
        print(f'turboSETI infile : \n {fileinfo}')

    # Select necessary columns
    filepaths   = fileinfo['filepath'].to_numpy()
    filenames   = fileinfo['filename'].to_numpy()
    target      = fileinfo['target_name'].to_numpy()
    tois        = fileinfo['toi'].to_numpy()

    # Also initiate cursor for updating the table later
    cursor = db.cursor()

    # Run turboSETI
    for ii, infile in zip(iis, filepaths[iis]):

        # start timer
        if t:
            start = time.time()

        # Set up output subdirectory
        outdir = os.path.join(outDir, f"TOI-{tois[ii]}")

        if not test:
            # Write to log file
            outlog = os.path.join(outdir, f'{tois[ii]}-cadence.log')
            with open(outlog, 'a') as f:
                f.write(f'Starting turboSETI for {infile}\n')

        if not test:

            # Make out directory if it doesn't exist
            print(outdir)
            if not os.path.exists(outdir):
                os.mkdir(outdir)

            # Run turboSETI
            fd = FindDoppler(infile, max_drift=4, snr=10, out_dir=outdir)
            fd.search(n_partitions=32)

        # End timer and write to spreadsheet if time is true
        if t:
            runtime = time.time() - start
            sqlcmd0 = f"UPDATE {sqlTable} SET runtime={runtime} WHERE row_num={ii}"
            cursor.execute(sqlcmd0)
            if not test:
                with open(outlog, 'a') as f:
                    f.write('{} Runtime : {}\n'.format(target[ii], runtime))

        # Write outfile path to dataframe
        name = filenames[ii].split('.')[0] + '.dat'
        sqlcmd1 = f"UPDATE {sqlTable} SET outpath='{os.path.join(outdir,name)}' WHERE row_num={ii}"
        cursor.execute(sqlcmd1)

        # Update spreadsheet to reflect turboSETI run
        sqlcmd2 = f"UPDATE {sqlTable} SET turboSETI='TRUE' WHERE row_num={ii}"
        cursor.execute(sqlcmd2)
        if not test:
            with open(outlog, 'a') as f:
                f.write(f'Finished running turboSETI on {infile}')
                f.write('\n')

        # Commit changes to database
        db.commit()

        if test:
            time.sleep(0.1)

def main():
    '''
    Access spreadsheet with file information data then run turboSETI on those
    files if it has not already been run. Outputs to subdirectories labelled by
    cadence ON target inside specified directory
    '''

    dir = '/datax2/scratch/noahf'

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ii', help='Array of indexes to run through turboSETI')
    parser.add_argument('--sqlTable', help='SQL table with data')
    parser.add_argument('--outdir', help='output directory', type=str, default=dir)
    parser.add_argument('--timer', help='Should the runtime be recorded', type=bool, default=True)
    parser.add_argument('--test', help='If true, script enters testing mode', type=bool, default=False)
    args = parser.parse_args()

    wrap_turboSETI(args.ii, args.outdir, args.sqlTable, t=args.timer, test=args.test)

if __name__ == '__main__':
    sys.exit(main())
