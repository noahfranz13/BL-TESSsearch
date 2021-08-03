import os, glob, sys
import subprocess as sp
import numpy as np

def getPaths():

    cmd = 'find /mnt_blc*/datax2/scratch/noahf/ -type d -name *TOI*'
    find = sp.Popen(cmd, stdout=sp.PIPE, shell=True)

    dirs = find.communicate()[0].split(b'\n')

    dirsToReturn = []
    for dir in dirs:
        dd = dir.decode()
        if dd[-7:] != '-copied':
            dirsToReturn.append(dd)

    return dirsToReturn

def getLen(dir):
    files = glob.glob(dir)
    return len(files)

def multiCommand(commands, slowdebug=False):
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
    for cmd in commands:

        ssh = sp.Popen(cmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
        ps.append(ssh)
        if slowdebug:
            print(ssh.stdout.readlines(), ssh.stderr.readlines())

    return ps

def main():

    allDirs = getPaths()
    condaenv = '/home/noahf/miniconda3/bin/activate'

    cmds = []
    for dd in allDirs:

        if len(dir) > 1:

            node = dd[5:10]

            cmd = ['ssh', node, f"source {condaenv} runTurbo ; python3 FindPlot.py --dir {dd[10:]}"]
            cmds.append(cmd)

    #print(cmds)
    ps = multiCommand(cmds)

    for p in ps:
        p.communicate()

if __name__ == '__main__':
    sys.exit(main())
