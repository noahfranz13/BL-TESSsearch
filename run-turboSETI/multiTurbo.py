# Imports
import os, sys, time
import subprocess as sp
import numpy as np
import pandas as pd

def splitRun(nnodes, debug, infile, t, outDir, splicedonly):

    if t:
        start = time.time()

    cwd = os.getcwd()
    print(f'Your cwd has been idetified as {cwd}')

    filepath = os.path.join(cwd, infile)
    fileinfo = pd.read_csv(filepath)

    if debug:
        print(f'infile: {fileinfo}')

    # Only select files that haven't been run through turboSETI
    turbo   = fileinfo['TurboSETI?'].to_numpy()
    spliced = fileinfo['SPLICED?'].to_numpy()

    if splicedonly:
        iis = np.where((turbo == False) * (spliced == 'spliced'))[0]
    else:
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

        cmd = ['ssh', cn[ii], f"source {condaenv} runTurbo ; python3 {cwd}/wrapTurbo.py --ii '{kk}' --infile {filepath} --timer {t} --outdir {outDir}"]

        ssh = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)

        if debug:
            print(ssh.stdout.readlines(), ssh.stderr.readlines())

        ps.append(ssh)

    for p in ps:
        p.communicate()

    if t:
        print(time.time()-start)

    if debug:
        outdata = pd.read_csv(filepath)
        print(outdata)
    
def main():
    '''
    Run turboSETI in parallel across multiple compute nodes on GBT
    Must pass in a csv file that can be read in with pandas and has headers with

    TurboSETI? : if the file has been run through turboSETI
    FILE PATH : path to turboSETI input file, inlcuding name
    FILE NAME : Just the name of the file being passed into turboSETI
    TARGET NAME : Name of target in the file passed into turboSETI
    TOI : on target of the cadence to specify the output directory
    SPLICED? : If the file is spliced of unspliced

    INPUT OPTIONS
    nnodes : number of compute nodes to run on, default is 64
    infile : infile with the headers above
    debug  : prints specific lines to help debug subprocess
    timer  : times the run if set to true, default is true
    outdir : output directory of turboSETI files, will consist of subdirectories
             labelled by TOI (ON target)

    RETURNS
    TurboSETI output files in subdirectories labelled by the ON target for each
    cadence. These subdirectories will be stored in directory specified by outdir

    '''

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--nnodes', help='Number of Compute nodes to run on', type=int, default=64)
    parser.add_argument('--infile', help='file with info about turboSETI runs', type=str, default='franz-turboSETI-input-file-info.csv')
    parser.add_argument('--debug', help='if true run script in debug mode', type=bool, default=False)
    parser.add_argument('--timer', help='times run if true', type=bool, default=True)
    parser.add_argument('--outdir', help='Output Directory for turboSETI files', type=str, default='/datax/scratch/noahf/turboSETI-outFiles')
    parser.add_argument('--splicedonly', help='Should it be run on only the spliced files', type=bool, default=False)
    args = parser.parse_args()

    splitRun(args.nnodes, args.debug, args.infile, args.timer, args.outdir, args.splicedonly)

if __name__ == '__main__':
    sys.exit(main())
