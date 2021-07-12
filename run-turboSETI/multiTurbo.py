# Imports
import os, sys, time
import subprocess as sp
import numpy as np
import pandas as pd
import pymysql

def splitRun(nnodes, debug, t, outDir, splicedonly):

    if t:
        start = time.time()

    cwd = os.getcwd()

    mysql = pymysql.connect(host=os.environ['GCP_IP'], user=os.environ['GCP_USR'],
                            password=os.environ['GCP_PASS'], database='FileTracking')

    if debug:
        query = '''
                SELECT row_num, turboSETI, splice
                FROM infiles_test
                '''
    else:
        query = '''
                SELECT turboSETI, splice
                FROM infiles
                '''

    fileinfo = pd.read_sql(query, mysql)

    if debug:
        print(f'table used : \n{fileinfo}')

    # Only select files that haven't been run through turboSETI
    turbo   = fileinfo['turboSETI'].to_numpy()
    spliced = fileinfo['splice'].to_numpy()

    if splicedonly:
        iis = np.where((turbo == 'FALSE') * (spliced == 'spliced'))[0]
    else:
        iis = np.where(turbo == 'FALSE')[0]

    if debug:
        print(f'indexes used: {iis}')

    # Split array of indexes into 2D array to run on separate cores
    if len(iis)%nnodes == 0:
        ii2D = np.reshape(iis, (nnodes, -1))
    else:
        nleft = len(iis)%nnodes
        ii2D = np.reshape(iis[:-nleft], (nnodes, -1)).tolist()
        for k in range(nleft):
            ii2D[k].append(iis[-(k+1)])
        ii2D = np.array(ii2D, dtype=object)

    # create list of compute nodes with length nnodes
    cn = []
    for i in range(8):
        for k in range(10):

            if i == 0:
                node = f'blc{k}'
            else:
                node = f'blc{i}{k}'

            if int(node[-1]) <= 7:
                cn.append(node)

    # Choose compute nodes starting with highest number
    cn = np.flip(cn)
    cn = cn[:nnodes]

    print(f'Running on compute nodes {min(cn)} to {max(cn)}')

    # Run on separate compute nodes
    ps = []
    for ii, node in zip(ii2D, cn):

        condaenv = '~/miniconda3/bin/activate'

        cmd = ['ssh', node, f"source {condaenv} runTurbo ; source /home/noahf/.bash_profile ; python3 {cwd}/wrapTurbo.py --ii '{ii}' --timer {t} --outdir {outDir} --test {debug}"]
        ssh = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)
        ps.append(ssh)
        if debug:
            print(ssh.stdout.readlines(), ssh.stderr.readlines())

    for p in ps:
        p.communicate()

    if t:
        print(time.time()-start)

def main():
    '''
    Run turboSETI in parallel across multiple compute nodes on GBT
    Must setup environment variables with access to a mysql database called
    FileTracking with the following columns

    turboSETI : if the file has been run through turboSETI
    filepath : path to turboSETI input file, inlcuding name
    filename : Just the name of the file being passed into turboSETI
    target_name : Name of target in the file passed into turboSETI
    toi : on target of the cadence to specify the output directory
    splice : If the file is spliced of unspliced

    INPUT OPTIONS
    nnodes      : number of compute nodes to run on, default is
    debug       : prints specific lines to help debug subprocess
    timer       : times the run if set to true, default is true
    outdir      : output directory of turboSETI files, will consist of subdirectories
                  labelled by TOI (ON target)
    splicedonly : If True only spliced files are run through

    Instead of passing in username, password, and IP of the database, make
    environment variables of
    GCP_IP   : IP address
    GCP_USR  : Username
    GCP_PASS : password

    RETURNS
    TurboSETI output files in subdirectories labelled by the ON target for each
    cadence. These subdirectories will be stored in directory specified by outdir

    '''

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--nnodes', help='Number of Compute nodes to run on', type=int, default=64)
    parser.add_argument('--debug', help='if true run script in debug mode', type=bool, default=False)
    parser.add_argument('--timer', help='times run if true', type=bool, default=True)
    parser.add_argument('--outdir', help='Output Directory for turboSETI files', type=str, default='/datax/scratch/noahf/turboSETI-outFiles')
    parser.add_argument('--splicedonly', help='Should it be run on only the spliced files', type=bool, default=False)
    args = parser.parse_args()

    splitRun(args.nnodes, args.debug, args.timer, args.outdir, args.splicedonly)

if __name__ == '__main__':
    sys.exit(main())
