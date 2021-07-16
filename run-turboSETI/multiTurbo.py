# Imports
import os, sys, time
import subprocess as sp
import numpy as np
import pandas as pd
import pymysql

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

def getIndex(sqlTable, splicedonly, unsplicedonly, debug=False):
    '''
    Get list of indexes to run turboSETI on

    sqlTable [str] : name of sql table to reference in FileTracking database
    splicedonly [bool] : if only the spliced files should be run through
    unsplicedonly [bool] : if only the spliced files should be run through
    debug [bool] : if True, print statements for debugging

    returns : list of indexes to run turboSETI on
    '''

    mysql = pymysql.connect(host=os.environ['GCP_IP'], user=os.environ['GCP_USR'],
                            password=os.environ['GCP_PASS'], database='FileTracking')

    query = f'''
            SELECT *
            FROM {sqlTable}
            WHERE turboSETI='FALSE'
            '''

    fileinfo = pd.read_sql(query, mysql)

    if debug:
        print(f'table used : \n{fileinfo}')

    # Create 2D array of indexes
    spliced = fileinfo['splice'].to_numpy()
    tois = fileinfo['toi'].to_numpy()

    uniqueIDs = np.unique(tois)
    ii2D = []
    for id in uniqueIDs:

        if splicedonly:
            arg = (spliced == 'spliced') * (tois == id)
        elif unsplicedonly:
            arg = (spliced == 'unspliced') * (tois == id)
        else:
            arg = (tois == id)

        whereID = np.where(arg)[0]
        ii2D.append(whereID)

    if debug:
        print(f'indexes used: {ii2D}')

    # Get number of files running through
    length = 0
    for row in ii2D:
        length+=len(row)
    print(f"Running turboSETI on {length} files")

    return ii2D

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
    '''
    Run turboSETI in parallel across multiple compute nodes on GBT
    Must setup environment variables with access to a mysql database as specified
    in README

    INPUT OPTIONS
    nnodes      : number of compute nodes to run on, default is
    debug       : prints specific lines to help debug subprocess
    timer       : times the run if set to true, default is true
    outdir      : output directory of turboSETI files, will consist of subdirectories
                  labelled by TOI (ON target)
    sqlTable    : name of SQL table
    splicedonly : If True only spliced files are run through
    unsplicedonly : If True only unspliced files are run through
    '''

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--nnodes', help='Number of Compute nodes to run on', type=int, default=64)
    parser.add_argument('--debug', help='if true run script in debug mode', type=bool, default=False)
    parser.add_argument('--timer', help='times run if true', type=bool, default=True)
    parser.add_argument('--outdir', help='Output Directory for turboSETI files', type=str, default='/datax2/scratch/noahf')
    parser.add_argument('--sqlTable', help='Table name in the sql database', type=str)
    parser.add_argument('--splicedonly', help='Should it be run on only the spliced files', type=bool, default=False)
    parser.add_argument('--unsplicedonly', help='Should it be run on only the spliced files', type=bool, default=False)
    parser.add_argument('--slowdebug', type=bool, default=False)
    args = parser.parse_args()

    if args.timer:
        start = time.time()

    condaenv = '/home/noahf/miniconda3/bin/activate'
    cwd = os.getcwd()
    varPath = '~/.bash_profile'

    print(f'Writing files to {args.outdir}')

    cns = getNodes(args.nnodes)
    ii2D = getIndex(args.sqlTable,
                    splicedonly=args.splicedonly,
                    unsplicedonly=args.unsplicedonly,
                    debug=args.debug)

    cmds = []
    nodes = []
    for node, ii in zip(cns, ii2D):

        if len(ii) != 0:

            print(f"Running turboSETI on {len(ii)} files on compute node: {node}")

            if args.debug:
                cmd = ['ssh', node, f"source {condaenv} runTurbo ; source {varPath} ; python3 {cwd}/wrapTurbo.py --ii '{ii.tolist()}' --timer {args.timer} --outdir {args.outdir} --test {args.debug} --sqlTable {args.sqlTable}"]
                print(f'Running: {cmd}')

            else:
                cmd = ['ssh', node, f"source {condaenv} runTurbo ; source {varPath} ; python3 {cwd}/wrapTurbo.py --ii '{ii.tolist()}' --timer {args.timer} --outdir {args.outdir} --sqlTable {args.sqlTable}"]

            cmds.append(cmd)
            nodes.append(node)

    ps = multiCommand(nodes, cmds, slowdebug=args.slowdebug)

    try:
        for p in ps:
            p.communicate()
    except KeyboardInterrupt:
        for p, cn in zip(ps, usedcn):
            exitcmd = ['ssh', cn, f"kill -9 $(pidof python3 {cwd}/wrapTurbo.py)"]
            exitssh = sp.Popen(exitcmd, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)

        print('All Processes Terminated')

    if args.timer:
        print(time.time()-start)

if __name__ == '__main__':
    sys.exit(main())
