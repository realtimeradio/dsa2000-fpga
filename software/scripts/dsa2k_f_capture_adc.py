#! /usr/bin/env python

"""
Capture blocks of 16k samples from both channels of an AD9207 ADC, and
write to csv.

Generated csv files have a three line header.
The first line contains the time the dump script was launched, in python `time.ctime()` string representation.
The second header line contains the ADC channels which were dumped, as a comma-separated list of ADC channels. With the current software, this is always "0,1".
The third line of the header contains custom text as supplied with the `--header` command line flag. It is empty if no custom header is supplied.

Following the header, each line of the file represents a sequence of 16k ADC samples which were captured.
Sequential lines cycle through multiple ADC channels (if a file contains more than one channel) and then through consecutive dumps.
For example, a file generated with the flags `-N 1` will generate a file with the following contents:

```
Wed May 10 11:29:58 2023
0,1

4,2,-4,3, ... -10,13 # 16k ADC samples from the first dump of channel 0
5,-10,20, ... 14,-19 # 16k ADC samples from the first dump of channel 1
# END OF FILE
```
"""

import time
import os
import sys
import argparse
import numpy as np
from dsa2k_f import IwaveFengine

DEFAULT_FPGFILE = '/home/jackh/src/dsa2000-fpga/firmware/src/models/dsa2k_iwave_adc_only/outputs/dsa2k_iwave_adc_only_2023-04-29_1224.fpg'
DEFAULT_HOST = '192.168.2.148'

def main(host, fpgfile, n_dumps, header="", outfile=None, force=False,):

    if not os.path.isfile(fpgfile):
        print(f"{fpgfile} doesn't exist. Exiting")
        exit()

    f = IwaveFengine(host)
    f.program(fpgfile) # This doesn't actually program the FPGA, but loads register map.

    t = int(time.time())
    if outfile is not None:
        filename = outfile
    else:
        filename = f"iwave_ad9207_dump_{t}.csv"
    print(f"Output file is {filename}")
    if not args.force:
        if os.path.exists(filename):
            print("File already exists. Use the -f flag to overwrite, or choose a different --outfile name")
            exit()

    chans = [0, 1] # Always 2 channels
    with open(filename, 'w') as fh:
        fh.write("%s\n" % time.ctime(t))
        fh.write("%s\n" % (','.join(map(str, chans))))
        fh.write("%s\n" % args.header)
    for i in range(n_dumps):
        print("Capturing %d of %d" % (i+1, n_dumps), file=sys.stderr)
        x = f.input.get_snapshot()
        with open(filename, 'a') as fh:
            np.savetxt(fh, x, fmt="%d", delimiter=",")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture ADC samples to csv file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fpgfile', type=str, default=DEFAULT_FPGFILE,
                        help='fpgfile running on FPGA')
    parser.add_argument('--host', type=str, default=DEFAULT_HOST,
                        help='FPGA hostname (or IP address) from which to read')
    parser.add_argument("--outfile", type=str, default=None,
                        help="Custom output filename. If None, use 'iwave_ad9207_dump_<timestamp>.csv'")
    parser.add_argument("--header", type=str, default="",
                        help="Custom header text to be written to the third line of output file")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force overwriting of any existing output file")
    parser.add_argument("-N", dest="n_dumps", type=int, default=0,
                        help="Number of captures to dump to disk. 0 for no file output")
    
    args = parser.parse_args()
    main(args.host,
         args.fpgfile,
         args.n_dumps,
         header=args.header,
         outfile=args.outfile,
         force=args.force)
