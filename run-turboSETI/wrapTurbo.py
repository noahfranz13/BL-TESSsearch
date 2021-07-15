# Imports
import os, sys, time, signal
import numpy as np
import pandas as pd
import pymysql
from turbo_seti.find_doppler.find_doppler import FindDoppler

def wrap_turboSETI(iis, outDir, sqlTable, t=True, test=False):
    '''
    iis : numpy array of indexes to run through
    outDir : directory to store output subdirectories
    sqlTable : input SQL table name
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
            WHERE turboSETI='FALSE'
            '''

    fileinfo = pd.read_sql(query, db)

    if test:
        print(f'turboSETI infile : \n {fileinfo}')

    # Select necessary columns
    filepaths   = fileinfo['filepath'].to_numpy()
    filenames   = fileinfo['filename'].to_numpy()
    target      = fileinfo['target_name'].to_numpy()
    tois        = fileinfo['toi'].to_numpy()
    row_num     = fileinfo['row_num'].to_numpy()

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

        # Also initiate cursor for updating the table later
        cursor = db.cursor()

        # End timer and write to spreadsheet

        name = filenames[ii].split('.')[0] + '.dat'

        if t:
            runtime = time.time() - start
            if not test:
                with open(outlog, 'a') as f:
                    f.write('{} Runtime : {}\n'.format(target[ii], runtime))

            sqlcmd = f"""
                      UPDATE {sqlTable}
                      SET runtime={runtime},
                          outpath='{os.path.join(outdir,name)}',
                          turboSETI='TRUE'
                      WHERE row_num={row_num[ii]}
                      """
            cursor.execute(sqlcmd)
            db.commit()

        else:
            sqlcmd = f"""
                      UPDATE {sqlTable}
                      SET outpath='{os.path.join(outdir,name)}',
                          turboSETI='TRUE'
                      WHERE row_num={row_num[ii]}
                      """
            cursor.execute(sqlcmd)
            db.commit()

        if not test:
            with open(outlog, 'a') as f:
                f.write(f'Finished running turboSETI on {infile}')
                f.write('\n')

        if test:
            time.sleep(0.1)

def SignalHandler(signum, frame):
    raise KeyboardInterrupt

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

    # Kill process if any of these signals are received
    signal.signal(signal.SIGHUP, SignalHandler)
    signal.signal(signal.SIGTERM, SignalHandler)
    #signal.signal(signal.SIGKILL, SignalHandler)
    signal.signal(signal.SIGINT, SignalHandler)

    wrap_turboSETI(args.ii, args.outdir, args.sqlTable, t=args.timer, test=args.test)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('got here')
        sys.exit(1)
