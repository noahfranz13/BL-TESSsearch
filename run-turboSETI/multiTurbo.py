# Imports
import os, sys, time
import subprocess as sp
import numpy as np
import pandas as pd

# Tunable Params
nnodes = 8

start = time.time()

filepath = os.path.join(os.getcwd(), 'franz-turboSETI-input-file-info.csv')
fileinfo = pd.read_csv(filepath)

# Only select files that haven't been run through turboSETI
turbo = fileinfo['TurboSETI?'].to_numpy()
iis = np.where(turbo == False)[0]

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

    condaenv = '/home/noahf/miniconda3/etc/profile.d/conda.sh'
    scPath = './BL-TESSsearch/run-turboSETI/wrapTurbo.py'
    cmd = ['ssh', cn[ii], 'source', condaenv, 'conda', 'activate', 'runTurbo', 'python3', scPath, f'--ii {kk}']

    p = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)
    print(p.stderr.readlines())
    ps.append(p)

for p in ps:
    p.communicate()

print(time.time()-start)
