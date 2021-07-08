# Imports
import os, sys, time
import subprocess as sp
import numpy as np
import pandas as pd

def splitRun(nnodes, debug, infile, t):

    if t:
        start = time.time()

    cwd = os.getcwd()
    print(f'Your cwd has been idetified as {cwd}')

    filepath = os.path.join(cwd, infile)
    fileinfo = pd.read_csv(filepath)

    if debug:
        print(f'infile: {fileinfo}')

    # Only select files that haven't been run through turboSETI
    turbo = fileinfo['TurboSETI?'].to_numpy()
    iis = np.where(turbo == False)[0]

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
    cn = cn[:nnodes]

    # Run on separate compute nodes
    ps = []
    for ii, kk in enumerate(ii2D):

        condaenv = '~/miniconda3/bin/activate' # '/home/noahf/miniconda3/etc/profile.d/conda.sh'

        cmd = ['ssh', cn[ii], f"source {condaenv} runTurbo ; python3 {cwd}/wrapTurbo.py --ii '{kk}' --infile {filepath} --timer {t}"]

        ssh = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)

        if debug:
            print(ssh.stdout.readlines(), ssh.stderr.readlines())

        ps.append(ssh)

    for p in ps:
        p.communicate()

    if t:
        print(time.time()-start)

def main():

    file = 'franz-turboSETI-input-file-info.csv'
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--nnodes', help='Number of Compute nodes to run on', type=int, default=64)
    parser.add_argument('--infile', help='file with info about turboSETI runs', type=str, default='franz-turboSETI-input-file-info.csv')
    parser.add_argument('--debug', help='if true run script in debug mode', type=bool, default=False)
    parser.add_argument('--timer', help='times run if true', type=bool, default=True)
    args = parser.parse_args()

    splitRun(args.nnodes, args.debug, args.infile, args.timer)

if __name__ == '__main__':
    sys.exit(main())
