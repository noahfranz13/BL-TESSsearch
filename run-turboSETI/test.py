# Script to test the subprocess Popen spawning method
def sleeper(p):
   import time as t
   print('Hello new compute node')
   t.sleep(p)

def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--period', type=int)
    args = parser.parse_args()

    sleeper(args.period)
