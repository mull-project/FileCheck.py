#!/usr/bin/env python3

import os
import sys

print(sys.argv[0])
if len(sys.argv) == 1:
    print("<check-file> not specified")
    exit(2)

check_file = sys.argv[1]
if not os.path.isfile(check_file):
    print("Could not open check file '{}': No such file or directory".format(check_file))
    exit(2)

if os.path.getsize(check_file) == 0:
    print("error: no check strings found with prefix 'CHECK:'", file=sys.stderr)
    exit(2)

if sys.stdin.isatty():
    print("CHECK: FileCheck error: '-' is empty.")
    print("FileCheck command line: {}".format(check_file))

for line in sys.stdin:
    file_empty = False
    # print(line.rstrip())

# print("FileCheck")
# print("{}:1:10: error: CHECK: expected string not found in input".format(match_file))
# print("; CHECK: foo")
# print("         ^")
# print("<stdin>:1:1: note: scanning from here")
# print("hello")
# print("^")
# print("<stdin>:1:3: note: possible intended match here")
# print("hello")
# print("  ^")
