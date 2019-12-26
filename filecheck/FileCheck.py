#!/usr/bin/env python3

import argparse
import os
import re
import sys

from collections import namedtuple
from difflib import SequenceMatcher
from enum import Enum

__version__ = '0.0.11'


class FailedCheck:
    def __init__(self, check, line_idx):
        self.check = check
        self.line_idx = line_idx


class CheckFailedException(BaseException):
    def __init__(self, failed_check):
        self.failed_check = failed_check


class CheckNOTIsLastException(BaseException):
    pass


class InputFinishedException(BaseException):
    def __init__(self):
        pass


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


def debug_print(string):
    # print(string)
    pass


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
    print("filecheck: Python port of LLVM's FileCheck, flexible pattern matching file verifier")
    print("https://github.com/stanislaw/FileCheck.py")
    print("Version: {}".format(__version__))


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
    debug_print("check dump")
    debug_print("\tcheck_type: {}".format(check.check_type))
    debug_print("\tmatch_type: {}".format(check.match_type))
    debug_print("\texpression: {}".format(check.expression))
    debug_print("\tsource_line: {}".format(check.source_line))
    debug_print("\tcheck_line_idx: {}".format(check.check_line_idx))
    debug_print("\tstart_index: {}".format(check.start_index))


class CheckResult(Enum):
    PASS = 1
    FAIL_SKIP_LINE = 2
    FAIL_FATAL = 3
    CHECK_NOT_MATCH = 4
    CHECK_NOT_WITHOUT_MATCH = 5


def check_line(line, current_check, match_full_lines):
    if current_check.check_type == CheckType.CHECK_EMPTY:
        if line != '':
            return CheckResult.FAIL_FATAL

    elif current_check.check_type == CheckType.CHECK:
        if current_check.match_type == MatchType.SUBSTRING:
            if match_full_lines:
                if current_check.expression != line:
                    return CheckResult.FAIL_SKIP_LINE
            else:
                if current_check.expression not in line:
                    return CheckResult.FAIL_SKIP_LINE

        elif current_check.match_type == MatchType.REGEX:
            if not re.search(current_check.expression, line):
                return CheckResult.FAIL_SKIP_LINE

    elif current_check.check_type == CheckType.CHECK_NEXT:
        if current_check.match_type == MatchType.SUBSTRING:
            if match_full_lines:
                if current_check.expression != line:
                    return CheckResult.FAIL_FATAL
            else:
                if current_check.expression not in line:
                    return CheckResult.FAIL_FATAL

        elif current_check.match_type == MatchType.REGEX:
            if not re.search(current_check.expression, line):
                return CheckResult.FAIL_FATAL

    elif current_check.check_type == CheckType.CHECK_NOT:
        if current_check.match_type == MatchType.SUBSTRING:
            if current_check.expression in line:
                return CheckResult.CHECK_NOT_MATCH
            else:
                return CheckResult.CHECK_NOT_WITHOUT_MATCH

        elif current_check.match_type == MatchType.REGEX:
            if re.search(current_check.expression, line):
                return CheckResult.CHECK_NOT_MATCH
            else:
                return CheckResult.CHECK_NOT_WITHOUT_MATCH

    return CheckResult.PASS


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

            check_regex = ".*{}:{}(.*)".format(check_prefix, strict_whitespace_match)
            check_match = re.search(check_regex, line)
            check_type = CheckType.CHECK
            if not check_match:
                check_regex = ".*{}-NEXT:{}(.*)".format(check_prefix, strict_whitespace_match)
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

            check_not_regex = ".*{}-NOT:{}(.*)".format(check_prefix, strict_whitespace_match)
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

            check_empty_regex = ".*{}-EMPTY:".format(check_prefix)
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
    # This variable is currently only used for CHECK-NOT checks which do not
    # necessarily fail with a last input line. So we have to keep the failing
    # line index.
    current_check_line_idx = None

    try:
        current_check = next(check_iterator)
    except StopIteration:
        error_message = "error: no check strings found with prefix '{}:'".format(check_prefix)
        print(error_message, file=sys.stderr)
        sys.stdout.flush()
        exit(2)

    current_scan_base = 0

    check_result = None

    # We don't need to read the full input in most of the cases because it is
    # usually much less check lines than the lines in the input.
    # But if we don't read the full input and exit while the input is still
    # being written to the pipe, we will get exit code 141 (caused by SIGPIPE).
    # This happens only when "set -o pipefail" is set and it looks like LIT
    # always does it by default.
    # We have created a minimal example that reproduces this and it seems like
    # there is nothing we can do on the Python's side except reading ALL of the
    # stdin's output.
    # TODO: Maybe there is still a better workaround for this but we see there
    # TODO: is nothing too bad about simply reading the stdin until end.
    # TODO: Performance implications?
    # "Getting exit code 141 when reading from stdin with a Python script with “set -o pipefail” set"
    # https://stackoverflow.com/questions/59436858/getting-exit-code-141-when-reading-from-stdin-with-a-python-script-with-set-o/59436997?noredirect=1#comment105058533_59436997
    input_lines = sys.stdin.readlines()
    stdin_input_iter = enumerate(input_lines)

    try:
        line_idx, line = next(stdin_input_iter)
    except StopIteration:
        print("CHECK: FileCheck error: '-' is empty.")
        print("FileCheck command line: {}".format(check_file))
        exit(2)

    try:
        current_not_checks = []
        failed_check = None

        while True:
            line = line.rstrip()
            if not args.strict_whitespace:
                line = canonicalize_whitespace(line)

            while True:
                if not failed_check:
                    for current_not_check in current_not_checks:
                        check_result = check_line(line,
                                                  current_not_check,
                                                  args.match_full_lines)
                        if check_result == CheckResult.CHECK_NOT_MATCH:
                            failed_check = FailedCheck(current_not_check, line_idx)

                check_result = check_line(line, current_check, args.match_full_lines)

                if check_result == CheckResult.FAIL_FATAL:
                    failed_check = FailedCheck(current_check, line_idx)
                    raise CheckFailedException(failed_check)

                elif check_result == CheckResult.PASS:
                    if failed_check:
                        raise CheckFailedException(failed_check)

                    current_not_checks.clear()
                    try:
                        current_check = next(check_iterator)
                    except StopIteration:
                        exit(0)

                    try:
                        line_idx, line = next(stdin_input_iter)
                        current_scan_base = line_idx
                        break
                    except StopIteration:
                        raise InputFinishedException

                elif check_result == CheckResult.CHECK_NOT_MATCH:
                    failed_check = FailedCheck(current_check, line_idx)
                    try:
                        current_not_checks.append(current_check)
                        current_check = next(check_iterator)
                        continue
                    except StopIteration:
                        raise CheckFailedException(failed_check)

                elif check_result == CheckResult.CHECK_NOT_WITHOUT_MATCH:
                    try:
                        current_not_checks.append(current_check)
                        current_check = next(check_iterator)
                        continue
                    except StopIteration:
                        raise CheckNOTIsLastException

                elif check_result == CheckResult.FAIL_SKIP_LINE:
                    try:
                        line_idx, line = next(stdin_input_iter)
                        break
                    except StopIteration:
                        failed_check = FailedCheck(current_check, line_idx)
                        raise CheckFailedException(failed_check)

                assert 0, "Should not reach here"
    except InputFinishedException:
        # We reach here if there is no input anymore and no check has failed so
        # far. This means we can remove all CHECK-NOT checks from the input
        # checks and see if there any other checks left.
        if current_check.check_type == CheckType.CHECK_NOT:
            still_actual_check = None
            for check in check_iterator:
                if check.check_type != CheckType.CHECK_NOT:
                    still_actual_check = check
                    break
            else:
                # No checks which are still actual have been found. Declare success.
                exit(0)

            current_check = still_actual_check
            current_check_line_idx = line_idx
    except CheckNOTIsLastException:
        # Here we catch the case when the last check is known to be CHECK-NOT.
        # We have to iterate over the remaining input lines and check them all
        # against this last check.
        try:
            while True:
                line_idx, line = next(stdin_input_iter)
                if check_line(line, current_check, args.match_full_lines) == \
                        CheckResult.CHECK_NOT_MATCH:
                    current_check_line_idx = line_idx
                    break
        except StopIteration:
            exit(0)

    except CheckFailedException as e:
        current_check = e.failed_check.check
        current_check_line_idx = e.failed_check.line_idx

    # CHECK-EMPTY is special: if there is no output anymore and this check is
    # the 1) current and 2) the last one we want to declare success.
    # Otherwise we switch to a next check, make it current and go to do error
    # reporting below.
    if current_check.check_type == CheckType.CHECK_EMPTY and \
            check_result == CheckResult.PASS:
        try:
            current_check = next(check_iterator)
            input_lines.append("")
            current_scan_base += 1
        except StopIteration:
            exit(0)

    # Error reporting part. By now we know that we have failed and we just want
    # to report a check that has failed.

    if current_check.check_type == CheckType.CHECK_EMPTY:
        last_read_line = input_lines[current_scan_base].rstrip()
        print("{}:{}:{}: error: CHECK-EMPTY: expected string not found in input"
              .format(check_file,
                      current_check.check_line_idx + 1,
                      len(current_check.source_line) + 1))
        print("{}".format(current_check.source_line))
        print("^".rjust(len(current_check.source_line) + 1))
        print("<stdin>:{}:{}: note: scanning from here".format(current_scan_base + 1, 1))
        print(last_read_line)
        print("^")

        exit(1)

    if current_check.check_type == CheckType.CHECK:
        assert current_scan_base < len(input_lines)

        # FileCheck prefers to show non-empty lines when printing
        # "Scanning from here" so we are skipping through empty lines if any.
        last_read_line = input_lines[current_scan_base].rstrip()
        while last_read_line == "" and current_scan_base < (len(input_lines) - 1):
            current_scan_base += 1
            last_read_line = input_lines[current_scan_base].rstrip()

        if current_check.match_type == MatchType.SUBSTRING or \
                current_check.match_type == MatchType.REGEX:
            print("{}:{}:{}: error: {}: expected string not found in input"
                  .format(check_file,
                          current_check.check_line_idx + 1,
                          current_check.start_index + 1,
                          check_prefix))

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))
            print("<stdin>:{}:{}: note: scanning from here".format(current_scan_base + 1, 1))
            print(last_read_line)
            print("^")

            # This is rather weird but it looks like with the REGEX case, the
            # FileCheck C++ only prints possible intended matches starting from
            # the line next to the current_scan_base (and only when such line
            # exists!).
            # TODO: this needs more real-world input.
            if current_check.match_type == MatchType.SUBSTRING or \
                    (current_check.match_type == MatchType.REGEX and
                     current_scan_base < (len(input_lines) - 1)):
                candidate_line = None
                candidate_line_idx = None
                current_best_ratio = 0
                for read_line_idx, read_line in enumerate(input_lines[current_scan_base:]):
                    similar_ratio = similar(read_line, current_check.expression)
                    if current_best_ratio < similar_ratio:
                        candidate_line = read_line.rstrip()
                        candidate_line_idx = current_scan_base + read_line_idx
                        current_best_ratio = similar_ratio
                if candidate_line:
                    caret_pos = len(candidate_line) // 2 + 1
                    print("<stdin>:{}:{}: note: possible intended match here".format(candidate_line_idx + 1, caret_pos))
                    print(candidate_line)
                    print("^".rjust(caret_pos, ' '))

            exit(1)

    if current_check.check_type == CheckType.CHECK_NOT:
        if (current_check.match_type == MatchType.SUBSTRING or
                current_check.match_type == MatchType.REGEX):
            assert current_check_line_idx != None
            last_read_line = input_lines[current_check_line_idx].rstrip()

            if not args.strict_whitespace:
                last_read_line = re.sub("\\s+", ' ', last_read_line).strip()

            print("{}:{}:{}: error: CHECK-NOT: excluded string found in input"
                  .format(check_file,
                          current_check.check_line_idx + 1,
                          current_check.start_index + 1))

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))
            print("<stdin>:{}:{}: note: found here".format(current_check_line_idx + 1, 1))
            print(last_read_line)

            if current_check.match_type == MatchType.SUBSTRING:
                match_pos = last_read_line.find(current_check.expression)
                assert match_pos != -1

                # TODO: check on lines which start with spaces
                highlight_line = "^".rjust(match_pos, ' ')
                print(highlight_line.ljust(len(current_check.expression), '~'))
            else:
                print("^".ljust(len(last_read_line), '~'))

            exit(1)

        assert 0, "Not implemented"

    if current_check.check_type == CheckType.CHECK_NEXT:
        last_read_line = input_lines[current_scan_base].rstrip()

        if current_check.match_type == MatchType.SUBSTRING or \
                current_check.match_type == MatchType.REGEX:
            matching_line_idx = -1
            for line_idx, line in enumerate(input_lines[current_scan_base:]):
                if current_check.expression in line:
                    matching_line_idx = current_scan_base + line_idx

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
                previous_matched_line = input_lines[current_scan_base - 1].rstrip()

                print("{}:{}:{}: error: CHECK-NEXT: is not on the line after the previous match"
                      .format(check_file,
                              current_check.check_line_idx + 1,
                              current_check.start_index + 1))
                print(current_check.source_line.rstrip())
                print("^".rjust(current_check.start_index + 1))

                matching_line = input_lines[matching_line_idx].rstrip()
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

        raise NotImplementedError()


if __name__ == "__main__":
    main()
