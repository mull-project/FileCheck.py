#!/usr/bin/env python3

import os
import sys

print(sys.argv[0])
if len(sys.argv) == 1:
    print("<check-file> not specified")
    exit(1)

match_file = sys.argv[1]
if not os.path.isfile(match_file):
    print("Could not open check file '{}': No such file or directory".format(match_file))
    exit(1)

file_empty = True
for line in sys.stdin:
    file_empty = False
    print(line.rstrip())

if file_empty:
    print("CHECK: FileCheck error: '-' is empty.")
    print("FileCheck command line: {}".format(match_file))
