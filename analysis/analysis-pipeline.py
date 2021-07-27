import os, glob, sys
import subprocess as sp
import numpy as np

def getPaths():
    cmd = ['find', '/mnt_blc*/datax2/scratch/noahf/', '-type d', '-name *TOI*']
    find = sp.run(cmd, stdout=sp.PIPE)
    return find.stdout

def getLen(dir):
    files = glob.glob(dir)
    return len(files)

def getNodes(nnodes):
    '''
    Get a list of compute nodes based on the number of nodes given
    nnodes [int] : number of nodes to run the commands on
    returns : list of compute nodes to run on at GBT
    '''

    # Create list of available compute nodes
    cn = []
    for i in range(8):
        for k in range(10):

            if i == 0:
                node = f'blc{k}'
            else:
                node = f'blc{i}{k}'

            if int(node[-1])<=7 and node!='blc47': # skip blc47 because it has an error
                cn.append(node)

    # Choose compute nodes starting with highest number
    cn = np.flip(cn)
    cn = cn[:nnodes]

    print(f'Running on compute nodes {min(cn)} to {max(cn)}')
    return cn

def multiCommand(nodes, commands, slowdebug=False):
    '''
    Run n commands on n compute nodes
    nodes [list] : list of compute nodes to run on
    commands [list] : list of commands to run on each compute nodes, the first
                      command will be run on the first compute node, etc.
    slowdebug [bool] : if True, prints subprocess output as it goes
    returns list of subprocess Popen objects, one for each compute node
    '''

    # Run on separate compute nodes
    ps = []
    for cmd, node in zip(commands, nodes):

        ssh = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
        ps.append(ssh)
        if slowdebug:
            print(ssh.stdout.readlines(), ssh.stderr.readlines())

    return ps

def main():

    allDirs = getPaths()

    for dir in allDirs:
        print(dir)

if __name__ == '__main__':
    sys.exit(main())
