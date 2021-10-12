import os, glob, sys
from turbo_seti.find_event.plot_dat import plot_dat
from turbo_seti import find_event as find
import numpy as np

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default=os.getcwd())
    parser.add_argument('--minHit', type=float, default=None)
    parser.add_argument('--maxHit', type=float, default=None)
    args = parser.parse_args()

    path = args.dir

    dat_files = glob.glob(path + "*.dat")

    min_hit = 1e9
    max_hit = 0

    if args.minHit == None or args.maxHit == None:
        for file in dat_files:
            tbl = find.read_dat(file)
            min_freq, max_freq = min(tbl["Freq"]), max(tbl["Freq"])
            if min_freq < min_hit:
                min_hit = min_freq
            if max_freq > max_hit:
                max_hit = max_freq

    else:
        min_hit = args.minHit
        max_hit = args.maxHit # set min and max hits by hand just to get this image

    print("Lowest frequency hit:  ", min_hit)
    print("Highext frequency hit: ", max_hit)

    plot_range = 2000*1e-6 # a 2000Hz width, adjusted to be in units of MHz

    freq_range = np.arange(np.round(min_hit, 2), np.round(max_hit), plot_range)

    outDir = path + "bautista-analysis/"
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    for center in freq_range:
        plot_dat(path + "dat-list.lst",
                 path + "h5-list.lst",
                 path + "events-list.csv",
                 outdir=outDir,
                 check_zero_drift=False,
                 alpha=0.65,
                 color="black",
                 window=(center-0.001, center+0.001))
if __name__ == '__main__':
    sys.exit(main())
