# Imports
import os, sys, time, signal
import subprocess as sp
import numpy as np
import pandas as pd
import pymysql
import fabric

def sshCommand(commands, hosts):
    '''
    Function connect to n compute nodes and run n commands

    commands [list] : list of commands to run on each compute node
    hosts [list] : list of hosts to connect to

    returns connection object and results unless KeyboardInterrupt
    '''

    if len(hosts) > 1:
        c = fabric.SerialGroup(hosts)
    else:
        c = fabric.Connection(hosts)

    try:
        results = []
        for command in commands:
            res = c.run(command)
            results.append(res)

        return c, results

    except KeyboardInterrupt:
        c.close()

def getNodes(n):
    '''
    n [int] : number of compute nodes to run on

    returns backwards list of n compute nodes
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

    cn = np.flip(cn)
    cn = cn[:n]

    return cn

def getFalseIndexes(sqlTable, cns):
    '''
    Get indexes of the sqlTable rows that have not been run through turboSETI

    sqlTable [string] : Name of sql table in GCP BL FileTracking SQL Database
    cns [list] : list of compute nodes to run on

    returns indexes
    '''

    mysql = pymysql.connect(host=os.environ['GCP_IP'], user=os.environ['GCP_USR'],
                            password=os.environ['GCP_PASS'], database='FileTracking')

    query = f'''
            SELECT *
            FROM {sqlTable}
            WHERE turboSETI='FALSE'
            '''
    cursor = mysql.cursor()

    fileinfo = pd.read_sql(query, mysql)

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

    # Write compute node to run on to SQL table
    for cn, ii in zip(cns, ii2D):
        sqlcmd = f'''
                 UPDATE {sqlTable}
                 SET compute_node={cn}
                 WHERE row_num={tuple(ii.tolist())}
                 '''
        cursor.execute(sqlcmd)

    # Commit once list is done
    mysql.commit()

    # Get number of files running through
    length = 0
    for row in ii2D:
        length+=len(row)
    print(f"Running turboSETI on {length} files")

    return ii2D

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
    parser.add_argument('--nnodes', help='number of copmute nodes', type=int, default=64)
    parser.add_argument('--sqlTable', help='name of SQL table to connect to', type=str)
    parser.add_argument('--outdir', help='Directory for turboSETI outfiles', type=str, default='/datax2/scratch/noahf')
    parser.add_argument('--timer', default=True)
    args = parser.parse_args()

    if args.timer:
        start = time.time()

    cns = getNodes(args.nnodes)
    iis = getFalseIndexes(args.sqlTable)

    varPath = '~/.bash_profile'
    condaenv = '/home/noahf/miniconda3/bin/activate'

    cmds = [f'source {condaenv} runTurbo',
            f'source {varPath}',
            f"python3 {os.getcwd()}/wrapTurbo.py --timer {args.timer} --outdir {args.outdir} --sqlTable {args.sqlTable}"]

    c, results = sshCommand(cmds, cns)

    if args.timer:
        print('Runtime: ', time.time()-start)

    print(results)



if __name__ == '__main__':
    sys.exit(main())
