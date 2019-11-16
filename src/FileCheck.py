#!/usr/bin/env python3

import os
import re
import sys

from collections import namedtuple
from enum import Enum


class MatchType(Enum):
    SUBSTRING = 1
    EXACT_STRING = 2
    REGEX = 3


class CheckType(Enum):
    CHECK = 1
    CHECK_NOT = 2
    CHECK_EMPTY = 3


Check = namedtuple("Check", "check_type match_type expression source_line start_index")

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

            match_type = MatchType.SUBSTRING

            regex_line = re.sub(r"\{\{(.*?)\}\}", r"\1", check_expression)

            if check_expression != regex_line:
                match_type = MatchType.REGEX
                check_expression = regex_line
            else:
                check_expression = re.sub("\\s+", ' ', check_expression).strip()

            check = Check(check_type=CheckType.CHECK,
                          match_type=match_type,
                          expression=check_expression,
                          source_line=line,
                          start_index=check_match.start(1))

            checks.append(check)

        check_match = re.search('; CHECK-NOT: (.*)', line)
        if check_match:
            check_expression = check_match.group(1)

            check = Check(check_type=CheckType.CHECK_NOT,
                          match_type=MatchType.SUBSTRING,
                          expression=check_expression,
                          source_line=line,
                          start_index=check_match.start(1))

            checks.append(check)

        check_match = re.search('; CHECK-EMPTY:', line)
        if check_match:
            check = Check(check_type=CheckType.CHECK_EMPTY,
                          match_type=MatchType.SUBSTRING,
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
        if current_check.match_type == MatchType.SUBSTRING:
            line = re.sub("\\s+", ' ', line).strip()

            if current_check.expression not in line:
                continue

        if current_check.match_type == MatchType.REGEX:
            if not re.search(current_check.expression, line):
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

if current_check.check_type == CheckType.CHECK:
    if current_check.match_type == MatchType.SUBSTRING:
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

    if current_check.match_type == MatchType.REGEX:
        print("{}:{}:{}: error: CHECK: expected string not found in input"
              .format(check_file, line_counter, current_check.start_index + 1))

        print(current_check.source_line.rstrip())
        print("          ^")
        print("<stdin>:?:?: note: scanning from here")
        print("TODO")
        print("^")
        exit(1)

    # print("foo: {}".format(line == "\n"))


