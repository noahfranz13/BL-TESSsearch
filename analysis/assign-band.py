import os, glob
import subprocess as sp
import numpy as np
from analysis_pipeline import getPaths, multiCommand
from blimpy.io.hdf_reader import H5Reader


def band(dir, tol=0.7):

    L = [1.10, 1.90]
    S = [1.80, 2.80]
    C = [4.00, 7.80]
    X = [7.80, 11.20]

    h5List = glob.glob(dir+'/*.h5')

    minFreqs = []
    maxFreqs = []
    for file in h5List:
        h5 = H5Reader(file, load_data=False)
        hdr = h5.read_header()

        maxf = hdr['fch1'] * 10**-3
        minf = maxf - np.abs(hdr['foff']*hdr['nchans'])*10**-3

        minFreqs.append(minf)
        maxFreqs.append(maxf)

    dirMinf = min(minFreqs)
    dirMaxf = max(maxFreqs)

    print(f'min frequency: {dirMinf}\nmax frequency: {dirMaxf}')

    if abs(dirMinf-L[0]) < tol and abs(dirMaxf-L[1]) < tol:
        return 'L'
    elif abs(dirMinf-S[0]) < tol and abs(dirMaxf-S[1]) < tol:
        return 'S'
    elif abs(dirMinf-C[0]) < tol and abs(dirMaxf-C[1]) < tol:
        return 'C'
    elif abs(dirMinf-X[0]) < tol and abs(dirMaxf-X[1]) < tol:
        return 'X'
    else:
        return 'NA'


def main():

    dirs = getPaths()

    cmds = []
    for dir in dirs:

        node = dir[5:10]
        cmd = ['ssh', node, f'mv {dir} {dir}_{band(dir)}']

        cmds.append(cmd)

    print(cmds)
    # ps = multiCommand(cmds)
    #
    # for p in ps:
    #     p.communicate()

if __name__ == '__main__':
    sys.exit(main())
