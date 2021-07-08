import numpy as np
import csv

targetLocs = np.loadtxt('targets-location.csv', dtype=str)
targets = np.loadtxt('target-list.csv', dtype=str)

whereTIC = {}

for target in targets:
    ticid = target[1:-1]
    listPaths = []

    print('starting on {}'.format(ticid))

    for path in targetLocs:
        if path.find(ticid) != -1:
            listPaths.append(path)

    whereTIC[ticid] = listPaths

print()
print(whereTIC)

outFile = 'known-TIC-paths.csv'
with open(outFile, 'w') as f:
   writer = csv.writer(f)
   for key, val in whereTIC.items():
      writer.writerow([key, val])
