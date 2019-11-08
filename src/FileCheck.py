#!/usr/bin/env python3

import os
import re
import sys

from collections import namedtuple
from enum import Enum


class CheckType(Enum):
    CHECK = 1
    CHECK_NOT = 2
    CHECK_EMPTY = 3


Check = namedtuple("Check", "check_type expression source_line start_index")

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
        line = line.rstrip()
        check_match = re.search('; CHECK: (.*)', line)
        if check_match:
            check_expression = check_match.group(1)

            check = Check(check_type=CheckType.CHECK,
                          expression=check_expression,
                          source_line=line,
                          start_index=check_match.start(1))

            checks.append(check)

        check_match = re.search('; CHECK-NOT: (.*)', line)
        if check_match:
            check_expression = check_match.group(1)

            check = Check(check_type=CheckType.CHECK_NOT,
                          expression=check_expression,
                          source_line=line,
                          start_index=check_match.start(1))

            checks.append(check)

        check_match = re.search('; CHECK-EMPTY:', line)
        if check_match:
            check = Check(check_type=CheckType.CHECK_EMPTY,
                          expression=None,
                          source_line=line,
                          start_index=-1)

            if len(checks) == 0:
                print("{}:{}:{}: error: found 'CHECK-EMPTY' without previous 'CHECK: line".format(check_file, 1, 3))
                print(line)
                print("  ^")
                exit(2)

            checks.append(check)

check_iterator = iter(checks)

line_counter = 0

current_check = None
try:
    current_check = next(check_iterator)
except StopIteration:
    print("error: no check strings found with prefix 'CHECK:'", file=sys.stderr)
    exit(2)

for line in sys.stdin:
    line_counter = 1

    if current_check.check_type == CheckType.CHECK_EMPTY:
        if line != '\n':
            assert 0, "Not implemented"

    if current_check.check_type == CheckType.CHECK:
        if current_check.expression not in line:
            continue

    try:
        current_check = next(check_iterator)
    except StopIteration:
        exit(0)

if line_counter == 0:
    print("CHECK: FileCheck error: '-' is empty.")
    print("FileCheck command line: {}".format(check_file))
    exit(2)

if current_check.check_type == CheckType.CHECK_EMPTY:
    exit(0)

if current_check.check_type == CheckType.CHECK and current_check.expression not in line:
    print("{}:{}:{}: error: CHECK: expected string not found in input"
          .format(check_file, line_counter, current_check.start_index + 1))

    print(current_check.source_line.rstrip())
    print("          ^")
    print("<stdin>:?:?: note: scanning from here")
    print("TODO")
    print("^")
    print("<stdin>:?:?: note: possible intended match here")
    print("TODO")
    print("  ^")
    exit(2)

    # print("foo: {}".format(line == "\n"))


