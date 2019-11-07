#!/usr/bin/env python3

import os
import re
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

checks = []
with open(check_file) as f:
    for line in f:
        check_match = re.search('; CHECK: (.*)', line)

        if check_match:
            check = check_match.group(1)
            checks.append((check, line))
            # print(check)

check_iterator = iter(checks)

line_counter = 0
for line in sys.stdin:
    line_counter = 1

    try:
        current_check = next(check_iterator)
    except StopIteration:
        exit(0)

    if current_check[0] not in line:
        print("{}:{}:10: error: CHECK: expected string not found in input".format(check_file, line_counter))
        print(current_check[1].rstrip())
        print("          ^")
        print("<stdin>:TODO:TODO: note: scanning from here")
        print("TODO")
        print("^")
        print("<stdin>:TODO:TODO: note: possible intended match here")
        print("TODO")
        print("  ^")
        exit(2)

    # print("foo: {}".format(line == "\n"))

if line_counter == 0:
    print("CHECK: FileCheck error: '-' is empty.")
    print("FileCheck command line: {}".format(check_file))
    exit(2)


