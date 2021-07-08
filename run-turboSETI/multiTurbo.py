# Imports
import os, sys, time
import subprocess as sp
import numpy as np
import pandas as pd

# Tunable Params
nnodes = 64

start = time.time()

filepath = os.path.join(os.getcwd(), 'franz-turboSETI-input-file-info.csv')
fileinfo = pd.read_csv(filepath)

# Only select files that haven't been run through turboSETI
turbo = fileinfo['TurboSETI?'].to_numpy()
iis = np.where(turbo == 'FALSE')[0]

# Split array of indexes into 2D array to run on separate cores
if len(iis)%nnodes == 0:
    ii2D = np.reshape(iis, (nnodes, -1))
else:
    nleft = len(iis)%nnodes
    print(nleft)
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

    cmd = ['ssh', cn[ii], 'python3', './BL-TESSsearch/run-turboSETI/wrapTurbo.py', f'--ii {kk}']

    p = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)
    ps.append(p)

for p in ps:
    p.communicate()

print(time.time()-start)
