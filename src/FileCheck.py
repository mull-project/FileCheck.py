#!/usr/bin/env python3

import sys

print(sys.argv[0])
if len(sys.argv) == 1:
    print("<check-file> not specified")
    exit(1)

for line in sys.stdin:
    print(line.rstrip())
