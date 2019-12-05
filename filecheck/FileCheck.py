#!/usr/bin/env python3

import argparse
import os
import re
import sys

from collections import namedtuple
from difflib import SequenceMatcher
from enum import Enum
from pkg_resources import DistributionNotFound, get_distribution


__project__ = 'filecheck'

try:
    __version__ = get_distribution(__project__).version
except DistributionNotFound:
    __version__ = '(local)'

VERSION = "{0} v{1}".format(__project__, __version__)


class MatchType(Enum):
    SUBSTRING = 1
    EXACT_STRING = 2
    REGEX = 3


class CheckType(Enum):
    CHECK = 1
    CHECK_NEXT = 2
    CHECK_NOT = 3
    CHECK_EMPTY = 4


Check = namedtuple("Check", "check_type match_type expression source_line check_line_idx start_index")


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def print_help():
    print("USAGE: filecheck [options] <check-file>")
    print("")

    print("OPTIONS:")
    print("")

    print("General options:")
    print("")
    print("  --match-full-lines             - Require all positive matches to cover an entire input line.")
    print("                                   Allows leading and trailing whitespace if --strict-whitespace")
    print("                                   is not also passed.")
    print("  --strict-whitespace            - Do not treat all horizontal whitespace as equivalent")
    print("")

    print("Generic options:")
    print("")
    print("--help                         - Display available options")


def print_version():
    print(VERSION)

def escape_non_regex_or_skip(match_obj):
    non_regex = match_obj.group('non_regex')
    if non_regex:
        return re.escape(non_regex)
    return match_obj.group()


def escape_non_regex_parts(check_expression):
    regex_line = re.sub(r"((?P<non_regex>[^\{{2}]+)|(?P<regex>\{\{(.*?)\}\}))",
                        escape_non_regex_or_skip,
                        check_expression)

    return regex_line


# By default, FileCheck canonicalizes input horizontal whitespace (spaces and
# tabs) which causes it to ignore these differences (a space will match a tab).
# The --strict-whitespace argument disables this behavior.
# https://llvm.org/docs/CommandGuide/FileCheck.html#cmdoption-filecheck-strict-whitespace
def canonicalize_whitespace(input):
    output = re.sub("\\s+", ' ', input)
    return output


def dump_check(check):
    print("check dump")
    print("\tcheck_type: {}".format(check.check_type))
    print("\tmatch_type: {}".format(check.match_type))
    print("\texpression: {}".format(check.expression))
    print("\tsource_line: {}".format(check.source_line))
    print("\tcheck_line_idx: {}".format(check.check_line_idx))
    print("\tstart_index: {}".format(check.start_index))


def main():
    # FileCheck always prints its first argument.
    filecheck_path = sys.argv[0]
    if os.path.exists(filecheck_path):
        filecheck_path = os.path.abspath(filecheck_path)

    print(filecheck_path)

    if len(sys.argv) == 1:
        print("<check-file> not specified")
        exit(2)

    for arg in sys.argv:
        if arg == '--help':
            print_help()
            exit(0)

    for arg in sys.argv:
        if arg == '--version':
            print_version()
            exit(0)

    check_file = sys.argv[1]
    if not os.path.isfile(check_file):
        sys.stdout.flush()
        err = "Could not open check file '{}': No such file or directory".format(check_file)
        print(err)
        exit(2)

    if os.path.getsize(check_file) == 0:
        sys.stdout.flush()
        print("error: no check strings found with prefix 'CHECK:'", file=sys.stderr)
        exit(2)

    parser = argparse.ArgumentParser()

    parser.add_argument('check_file_arg', type=str, help='TODO')
    parser.add_argument('--strict-whitespace', action='store_true', help='TODO')
    parser.add_argument('--match-full-lines', action='store_true', help='TODO')
    parser.add_argument('--check-prefix', action='store', help='TODO')

    args = parser.parse_args()

    check_prefix = args.check_prefix if args.check_prefix else "CHECK"

    if not re.search('^[A-Za-z][A-Za-z0-9-_]+$', check_prefix):
        sys.stdout.flush()
        error_message = "Supplied check-prefix is invalid! Prefixes must be unique and start with a letter and contain only alphanumeric characters, hyphens and underscores"
        print(error_message, file=sys.stderr)
        exit(2)

    checks = []
    with open(check_file) as f:
        for line_idx, line in enumerate(f):
            line = line.rstrip()

            if not args.strict_whitespace:
                line = canonicalize_whitespace(line)

            # CHECK and CHECK-NEXT
            strict_whitespace_match = "" if args.strict_whitespace and args.match_full_lines else " ?"

            check_regex = "; {}:{}(.*)".format(check_prefix, strict_whitespace_match)
            check_match = re.search(check_regex, line)
            check_type = CheckType.CHECK
            if not check_match:
                check_regex = "; {}-NEXT:{}(.*)".format(check_prefix, strict_whitespace_match)
                check_match = re.search(check_regex, line)
                check_type = CheckType.CHECK_NEXT

            if check_match:
                check_expression = check_match.group(1)

                match_type = MatchType.SUBSTRING

                if re.search(r"\{\{.*\}\}", check_expression):
                    regex_line = escape_non_regex_parts(check_expression)
                    regex_line = re.sub(r"\{\{(.*?)\}\}", r"\1", regex_line)
                    match_type = MatchType.REGEX
                    check_expression = regex_line

                check = Check(check_type=check_type,
                              match_type=match_type,
                              expression=check_expression,
                              source_line=line,
                              check_line_idx=line_idx,
                              start_index=check_match.start(1))

                checks.append(check)
                continue

            check_not_regex = "; {}-NOT: (.*)".format(check_prefix)
            check_match = re.search(check_not_regex, line)
            if check_match:
                match_type = MatchType.SUBSTRING

                check_expression = check_match.group(1)

                if re.search(r"\{\{.*\}\}", check_expression):
                    regex_line = escape_non_regex_parts(check_expression)
                    regex_line = re.sub(r"\{\{(.*?)\}\}", r"\1", regex_line)
                    match_type = MatchType.REGEX
                    check_expression = regex_line

                check = Check(check_type=CheckType.CHECK_NOT,
                              match_type=match_type,
                              expression=check_expression,
                              source_line=line,
                              check_line_idx=line_idx,
                              start_index=check_match.start(1))

                checks.append(check)
                continue

            check_empty_regex = "; {}-EMPTY:".format(check_prefix)
            check_match = re.search(check_empty_regex, line)
            if check_match:
                check = Check(check_type=CheckType.CHECK_EMPTY,
                              match_type=MatchType.SUBSTRING,
                              expression=None,
                              source_line=line,
                              check_line_idx=line_idx,
                              start_index=-1)

                if len(checks) == 0:
                    print("{}:{}:{}: error: found 'CHECK-EMPTY' without previous 'CHECK: line".format(check_file, 1, 3))
                    print(line)
                    print("  ^")
                    exit(2)

                checks.append(check)
                continue

    check_iterator = iter(checks)

    current_check = None
    try:
        current_check = next(check_iterator)
    except StopIteration:
        error_message = "error: no check strings found with prefix '{}:'".format(check_prefix)
        print(error_message, file=sys.stderr)
        sys.stdout.flush()
        exit(2)

    line_counter = 0

    input_lines = []

    current_scan_base = 0

    stdin_input_iter = enumerate(sys.stdin)
    for line_idx, line in stdin_input_iter:
        line = line.rstrip()
        if not args.strict_whitespace:
            line = canonicalize_whitespace(line)

        input_lines.append(line)

        line_counter = line_counter + 1

        if current_check.check_type == CheckType.CHECK_EMPTY:
            if line != '':
                assert 0, "Not implemented"

        elif current_check.check_type == CheckType.CHECK:
            if current_check.match_type == MatchType.SUBSTRING:
                if args.match_full_lines:
                    if current_check.expression != line:
                        continue
                else:
                    if current_check.expression not in line:
                        continue

            elif current_check.match_type == MatchType.REGEX:
                if not re.search(current_check.expression, line):
                    continue

        elif current_check.check_type == CheckType.CHECK_NEXT:
            if current_check.match_type == MatchType.SUBSTRING:
                if not args.strict_whitespace:
                    line = re.sub("\\s+", ' ', line).strip()

                if args.match_full_lines:
                    if current_check.expression != line:
                        break
                else:
                    if current_check.expression not in line:
                        break

            elif current_check.match_type == MatchType.REGEX:
                if not re.search(current_check.expression, line):
                    break

        elif current_check.check_type == CheckType.CHECK_NOT:
            if current_check.match_type == MatchType.SUBSTRING:
                if not args.strict_whitespace:
                    line = re.sub("\\s+", ' ', line).strip()

                if current_check.expression in line:
                    break

            elif current_check.match_type == MatchType.REGEX:
                if re.search(current_check.expression, line):
                    break

        try:
            current_check = next(check_iterator)
            current_scan_base = line_idx + 1
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
            last_read_line = input_lines[current_scan_base]

            candidate_line = None
            current_best_ratio = 0
            for read_line in input_lines[current_scan_base:]:
                similar_ratio = similar(last_read_line, current_check.expression)
                if current_best_ratio < similar_ratio:
                    candidate_line = read_line
                    current_best_ratio = similar_ratio
            assert candidate_line

            print("{}:{}:{}: error: CHECK: expected string not found in input"
                  .format(check_file,
                          current_check.check_line_idx + 1,
                          current_check.start_index + 1))

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))
            print("<stdin>:{}:{}: note: scanning from here".format(current_scan_base + 1, 1))
            print(last_read_line)
            print("^")

            caret_pos = len(candidate_line) // 2 + 1
            print("<stdin>:{}:{}: note: possible intended match here".format(current_scan_base + 1, caret_pos))
            print(candidate_line)
            print("^".rjust(caret_pos, ' '))
            exit(1)

        if current_check.match_type == MatchType.REGEX:
            print("{}:{}:{}: error: CHECK: expected string not found in input"
                  .format(check_file,
                          current_check.check_line_idx + 1,
                          current_check.start_index + 1))

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))
            print("<stdin>:{}:{}: note: scanning from here".format(current_scan_base + 1, 1))
            print(line)
            print("^")
            exit(1)

    if current_check.check_type == CheckType.CHECK_NOT:
        if (current_check.match_type == MatchType.SUBSTRING or
                current_check.match_type == MatchType.REGEX):
            last_read_line = input_lines[-1]

            if not args.strict_whitespace:
                last_read_line = re.sub("\\s+", ' ', last_read_line).strip()

            print("{}:{}:{}: error: CHECK-NOT: excluded string found in input"
                  .format(check_file,
                          current_check.check_line_idx + 1,
                          current_check.start_index + 1))

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))
            print("<stdin>:{}:{}: note: found here".format(current_scan_base + 1, 1))
            print(last_read_line)

            if current_check.match_type == MatchType.SUBSTRING:
                match_pos = last_read_line.find(current_check.expression)
                assert match_pos != -1

                highlight_line = "^".rjust(match_pos, ' ')
                print("^".ljust(len(current_check.expression), '~'))
            else:
                print("^".ljust(len(last_read_line), '~'))

            exit(1)

        assert 0, "Not implemented"

    if current_check.check_type == CheckType.CHECK_NEXT:
        last_read_line = input_lines[current_scan_base]

        if current_check.match_type == MatchType.SUBSTRING:
            matching_line_idx = -1
            for line_idx, line in stdin_input_iter:
                line = line.rstrip()
                input_lines.append(line)

                if current_check.expression in line:
                    matching_line_idx = line_idx

            if matching_line_idx == -1:
                print("{}:{}:{}: error: CHECK-NEXT: expected string not found in input"
                      .format(check_file,
                              current_check.check_line_idx + 1,
                              current_check.start_index + 1))

                print(current_check.source_line.rstrip())
                print("^".rjust(current_check.start_index + 1))
                print("<stdin>:{}:{}: note: scanning from here".format(current_scan_base + 1, 1))
                print(last_read_line)
                print("^")

                exit(1)
            else:
                assert current_scan_base > 0
                previous_matched_line = input_lines[current_scan_base - 1]

                print("{}:{}:{}: error: CHECK-NEXT: is not on the line after the previous match"
                      .format(check_file,
                              current_check.check_line_idx + 1,
                              current_check.start_index + 1))
                print(current_check.source_line.rstrip())
                print("^".rjust(current_check.start_index + 1))

                matching_line = input_lines[matching_line_idx]
                print("<stdin>:{}:1: note: 'next' match was here".format(matching_line_idx + 1))
                print(matching_line)
                print("^")

                print("<stdin>:{}:{}: note: previous match ended here".format(current_scan_base, len(previous_matched_line) + 1))
                print(previous_matched_line)
                print("^".rjust(len(previous_matched_line) + 1))
                print("<stdin>:{}:{}: note: non-matching line after previous match is here".format(current_scan_base + 1, 1))
                print(last_read_line)
                print("^")

                exit(1)

        assert 0, "Not implemented"


if __name__ == "__main__":
    main()
