#!/usr/bin/env python3

import os
import re
import sys

from enum import Enum

class CheckType(Enum):
    CHECK = 1
    CHECK_NOT = 2

# FileCheck always prints its first argument.
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
            checks.append((check, line, check_match.start(1), CheckType.CHECK))

        check_match = re.search('; CHECK-NOT: (.*)', line)
        if check_match:
            check = check_match.group(1)
            checks.append((check, line, check_match.start(1), CheckType.CHECK_NOT))


check_iterator = iter(checks)

line_counter = 0

current_check = None
try:
    current_check = next(check_iterator)
except StopIteration:
    pass

if not current_check:
    print("error: no check strings found with prefix 'CHECK:'", file=sys.stderr)
    exit(2)

for line in sys.stdin:
    line_counter = 1

    if current_check[0] in line and current_check[3] == CheckType.CHECK:
        try:
            current_check = next(check_iterator)
        except StopIteration:
            exit(0)

if line_counter == 0:
    print("CHECK: FileCheck error: '-' is empty.")
    print("FileCheck command line: {}".format(check_file))
    exit(2)

if current_check[0] not in line and current_check[3] == CheckType.CHECK:
    print("{}:{}:{}: error: CHECK: expected string not found in input"
          .format(check_file, line_counter, current_check[2] + 1))

    print(current_check[1].rstrip())
    print("          ^")
    print("<stdin>:?:?: note: scanning from here")
    print("TODO")
    print("^")
    print("<stdin>:?:?: note: possible intended match here")
    print("TODO")
    print("  ^")
    exit(2)

    # print("foo: {}".format(line == "\n"))


