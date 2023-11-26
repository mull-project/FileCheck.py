#!/usr/bin/env python3

import argparse
import io
import os
import re
import sys

from difflib import SequenceMatcher
from enum import Enum

__version__ = "0.0.24"

from typing import Optional, List, Iterable


class FailedCheck:
    def __init__(self, check, line_idx):
        self.check = check
        self.line_idx = line_idx


class FailedImplicitCheckContext:
    def __init__(self, check, line, line_idx):
        self.check = check
        self.line = line
        self.line_idx = line_idx


class CheckFailedException(BaseException):
    def __init__(self, failed_check):
        super().__init__()
        self.failed_check = failed_check


class ImplicitCheckNotFailedException(BaseException):
    def __init__(self, failed_check_context):
        super().__init__()
        self.failed_check_context = failed_check_context


class CheckNOTIsLastException(BaseException):
    pass


class InputFinishedException(BaseException):
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


class Check:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        check_type: CheckType,
        match_type: MatchType,
        check_keyword: str,
        expression: Optional[str],
        source_line: str,
        check_line_idx: int,
        start_index: int,
    ):
        self.check_type = check_type
        self.match_type = match_type
        self.check_keyword = check_keyword
        self.expression = expression
        self.source_line = source_line
        self.check_line_idx = check_line_idx
        self.start_index = start_index

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            "Check("
            f"check_type: {self.check_type}, "
            f"match_type: {self.match_type}, "
            f"check_keyword: {self.check_keyword}, "
            f"expression: {self.expression}, "
            f"source_line: {self.source_line}, "
            f"check_line_idx: {self.check_line_idx}, "
            f"start_index: {self.start_index}"
            ")"
        )


class ImplicitCheck:
    def __init__(self, original_check: str, check: str):
        self.original_check = original_check
        self.check = check


LINE_NUMBER_REGEX = r"\[\[# +@LINE *([+-])? *([0-9]+)? *\]\]"


def similar(lhs, rhs):
    return SequenceMatcher(None, lhs, rhs).ratio()


def print_help():
    print("USAGE: filecheck [options] <check-file>")
    print("")

    print("OPTIONS:")
    print("")

    print("General options:")
    print("")
    print(
        "  --match-full-lines             - Require all positive matches to "
        "cover an entire input line."
    )
    print(
        "                                   Allows leading and trailing "
        "whitespace if --strict-whitespace"
    )
    print("                                   is not also passed.")
    print(
        "  --strict-whitespace            - Do not treat all horizontal "
        "whitespace as equivalent"
    )
    print("")

    print("Generic options:")
    print("")
    print("--help                         - Display available options")


def print_version():
    print(
        "filecheck: Python port of LLVM's FileCheck, "
        "flexible pattern matching file verifier"
    )
    print("https://github.com/mull-project/FileCheck.py")
    print(f"Version: {__version__}")


def escape_non_regex_or_skip(match_obj):
    non_regex = match_obj.group("non_regex")
    if non_regex:
        return re.escape(non_regex)
    return match_obj.group()


def escape_non_regex_parts(check_expression):
    regex_line = re.sub(
        r"((?P<non_regex>[^\{{2}]+)|(?P<regex>\{\{(.*?)\}\}))",
        escape_non_regex_or_skip,
        check_expression,
    )

    return regex_line


# By default, FileCheck canonicalizes input horizontal whitespace (spaces and
# tabs) which causes it to ignore these differences (a space will match a tab).
# The --strict-whitespace argument disables this behavior.
# https://llvm.org/docs/CommandGuide/FileCheck.html#cmdoption-filecheck-strict-whitespace
def canonicalize_whitespace(input_string):
    return re.sub("\\s+", " ", input_string)


class CheckResult(Enum):
    PASS = 1
    FAIL_SKIP_LINE = 2
    FAIL_FATAL = 3
    CHECK_NOT_MATCH = 4
    CHECK_NOT_WITHOUT_MATCH = 5


def check_line(
    line, current_check, match_full_lines
):  # pylint: disable=too-many-return-statements
    if current_check.check_type == CheckType.CHECK_EMPTY:
        if line != "":
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
            return CheckResult.CHECK_NOT_WITHOUT_MATCH

        if current_check.match_type == MatchType.REGEX:
            if re.search(current_check.expression, line):
                return CheckResult.CHECK_NOT_MATCH
            return CheckResult.CHECK_NOT_WITHOUT_MATCH

    return CheckResult.PASS


def implicit_check_line(check_not_check, strict_mode, line):
    if strict_mode:
        if check_not_check.original_check in line:
            return True
    elif check_not_check.check in line:
        return True
    return False


class CheckParserEmptyCheckException(BaseException):
    def __init__(self, check: Check):
        super().__init__()
        self.check = check


class Config:
    def __init__(  # pylint: disable = too-many-arguments
        self,
        check_file: str,
        match_full_lines: bool,
        strict_whitespace: bool,
        check_prefix: Optional[str],
        implicit_check_not: Optional[str],
        dump_input: Optional[str],
    ):
        self.check_file: str = check_file
        self.match_full_lines: bool = match_full_lines
        self.strict_whitespace: bool = strict_whitespace
        self.check_prefix: Optional[str] = (
            check_prefix if check_prefix else "CHECK"
        )
        self.implicit_check_not: Optional[str] = implicit_check_not
        self.dump_input: Optional[str] = dump_input
        self.strict_mode = match_full_lines and strict_whitespace

    @staticmethod
    def create_parser():
        parser = argparse.ArgumentParser()

        parser.add_argument("check_file_arg", type=str, help="TODO")
        parser.add_argument(
            "--strict-whitespace", action="store_true", help="TODO"
        )
        parser.add_argument(
            "--match-full-lines", action="store_true", help="TODO"
        )
        parser.add_argument("--check-prefix", action="store", help="TODO")
        parser.add_argument(
            "--implicit-check-not", action="append", help="TODO"
        )
        parser.add_argument(
            "--dump-input", action="store", choices=["fail"], help="TODO"
        )
        return parser

    @staticmethod
    def create(args):
        return Config(
            check_file=args.check_file_arg,
            match_full_lines=args.match_full_lines,
            strict_whitespace=args.strict_whitespace,
            check_prefix=args.check_prefix,
            implicit_check_not=args.implicit_check_not,
            dump_input=args.dump_input,
        )


class CheckParser:
    @staticmethod
    def parse_checks_from_file(
        check_file_path: str, config: Config
    ) -> List[Check]:
        with open(check_file_path, encoding="utf-8") as check_file:
            return CheckParser.parse_checks_from_strings(check_file, config)

    @staticmethod
    def parse_checks_from_strings(
        input_strings: Iterable[str], config: Config
    ) -> List[Check]:
        checks = []
        for line_idx, line in enumerate(input_strings):
            check = CheckParser.parse_check(line, line_idx, config)
            if check is None:
                continue
            if check.check_type == CheckType.CHECK_EMPTY and len(checks) == 0:
                raise CheckParserEmptyCheckException(check)
            checks.append(check)
        return checks

    @staticmethod
    def parse_check(line: str, line_idx, config: Config) -> Optional[Check]:
        # Allow check prefixes only at the beginnings of lines or
        # after non-word characters.
        # /^((?!PART).)*$/ is a negative match.
        # https://stackoverflow.com/a/6259570/598057
        before_prefix = f"^(((?!{config.check_prefix}).)*?[^-\\w])?"
        line = line.rstrip()

        if not config.strict_whitespace:
            line = canonicalize_whitespace(line)

        # CHECK and CHECK-NEXT
        strict_whitespace_match = "" if config.strict_mode else " *"

        check_regex = (
            f"{before_prefix}({config.check_prefix}):"
            f"{strict_whitespace_match}(.*)"
        )
        check_match = re.search(check_regex, line)
        check_type = CheckType.CHECK
        if not check_match:
            check_regex = (
                f"{before_prefix}({config.check_prefix}-NEXT):"
                f"{strict_whitespace_match}(.*)"
            )
            check_match = re.search(check_regex, line)
            check_type = CheckType.CHECK_NEXT

        if check_match:
            check_keyword = check_match.group(3)
            check_expression = check_match.group(4)
            if not config.strict_mode:
                check_expression = check_expression.strip(" ")

            match_type = MatchType.SUBSTRING

            if re.search(r"\{\{.*\}\}", check_expression):
                regex_line = escape_non_regex_parts(check_expression)
                regex_line = re.sub(r"\{\{(.*?)\}\}", r"\1", regex_line)
                match_type = MatchType.REGEX
                check_expression = regex_line
                if config.strict_mode:
                    if check_expression[0] != "^":
                        check_expression = "^" + check_expression
                    if check_expression[-1] != "$":
                        check_expression = check_expression + "$"

            # Replace line number expressions, e.g. `[[# @LINE + 3 ]]`
            line_var_match = re.search(LINE_NUMBER_REGEX, check_expression)
            while line_var_match is not None:
                offset = int(line_var_match.group(2) or 0)
                if line_var_match.group(1) == "-":
                    offset = -offset
                check_expression = re.sub(
                    LINE_NUMBER_REGEX,
                    str(line_idx + offset + 1),
                    check_expression,
                    count=1,
                )
                line_var_match = re.search(LINE_NUMBER_REGEX, check_expression)

            check = Check(
                check_type=check_type,
                match_type=match_type,
                check_keyword=check_keyword,
                expression=check_expression,
                source_line=line,
                check_line_idx=line_idx,
                start_index=check_match.start(4),
            )
            return check

        check_not_regex = (
            f"{before_prefix}({config.check_prefix}-NOT):"
            f"{strict_whitespace_match}(.*)"
        )
        check_match = re.search(check_not_regex, line)
        if check_match:
            match_type = MatchType.SUBSTRING

            check_keyword = check_match.group(3)
            check_expression = check_match.group(4)
            if not config.strict_mode:
                check_expression = check_expression.strip(" ")

            if re.search(r"\{\{.*\}\}", check_expression):
                regex_line = escape_non_regex_parts(check_expression)
                regex_line = re.sub(r"\{\{(.*?)\}\}", r"\1", regex_line)
                match_type = MatchType.REGEX
                check_expression = regex_line

            check = Check(
                check_type=CheckType.CHECK_NOT,
                match_type=match_type,
                check_keyword=check_keyword,
                expression=check_expression,
                source_line=line,
                check_line_idx=line_idx,
                start_index=check_match.start(4),
            )
            return check

        check_empty_regex = f"{before_prefix}({config.check_prefix}-EMPTY):"
        check_match = re.search(check_empty_regex, line)
        if check_match:
            check_keyword = check_match.group(3)

            check = Check(
                check_type=CheckType.CHECK_EMPTY,
                match_type=MatchType.SUBSTRING,
                check_keyword=check_keyword,
                expression=None,
                source_line=line,
                check_line_idx=line_idx,
                start_index=check_match.start(3),
            )
            return check

        return None


def main():
    # Force UTF-8 to be sent to stdout.
    # https://stackoverflow.com/a/3597849/598057
    sys.stdout = open(  # pylint: disable=consider-using-with
        1, "w", encoding="utf-8", closefd=False
    )

    input_lines = None

    # TODO: Unify exit_handler() handling.
    def exit_handler(code):
        # Here we diverge from LLVM FileCheck by printing input lines without
        # any additional formatting and hints.
        # Eventually it would be great to implement the same behavior.
        # https://llvm.org/docs/CommandGuide/FileCheck.html#cmdoption-filecheck-dump-input
        if code != 0 and input_lines and config.dump_input:
            print("")
            print("Full input was:")
            for input_line in input_lines:
                print(input_line.rstrip())
        sys.exit(code)

    if len(sys.argv) == 1:
        print("<check-file> not specified")
        exit_handler(2)

    for arg in sys.argv:
        if arg == "--help":
            print_help()
            exit_handler(0)

    for arg in sys.argv:
        if arg == "--version":
            print_version()
            exit_handler(0)

    check_file_path = sys.argv[1]
    if not os.path.isfile(check_file_path):
        sys.stdout.flush()
        err = (
            f"Could not open check file '{check_file_path}': "
            f"No such file or directory"
        )
        print(err)
        exit_handler(2)

    if os.path.getsize(check_file_path) == 0:
        sys.stdout.flush()
        print(
            "error: no check strings found with prefix 'CHECK:'",
            file=sys.stderr,
        )
        exit_handler(2)

    parser = Config.create_parser()
    config = Config.create(parser.parse_args())

    strict_mode = config.match_full_lines and config.strict_whitespace

    implicit_check_not_checks = []

    if config.implicit_check_not:
        for implicit_check_not_arg in config.implicit_check_not:
            # LLVM FileCheck does rstrip() here for some reason that
            # does not seem reasonable. We still prefer to be compatible.
            stripped_check = implicit_check_not_arg.rstrip()

            implicit_check_not = ImplicitCheck(
                original_check=implicit_check_not_arg, check=stripped_check
            )
            implicit_check_not_checks.append(implicit_check_not)

    if not re.search("^[A-Za-z][A-Za-z0-9-_]+$", config.check_prefix):
        sys.stdout.flush()
        error_message = (
            "Supplied check-prefix is invalid! Prefixes must be unique and "
            "start with a letter and contain only alphanumeric characters, "
            "hyphens and underscores"
        )
        print(error_message, file=sys.stderr)
        exit_handler(2)

    try:
        checks = CheckParser.parse_checks_from_file(check_file_path, config)
    except CheckParserEmptyCheckException as exception:
        print(
            f"{check_file_path}:"
            f"{exception.check.check_line_idx + 1}:"
            f"{exception.check.start_index + 1}: "
            f"error: "
            f"found 'CHECK-EMPTY' without previous 'CHECK: line"
        )
        print(exception.check.source_line)
        print("^".rjust(exception.check.start_index + 1, " "))
        exit_handler(2)

    check_iterator = iter(checks)

    current_check = None
    # This variable is currently only used for CHECK-NOT checks which do not
    # necessarily fail with a last input line. So we have to keep the failing
    # line index.
    current_check_line_idx = None

    try:
        current_check = next(check_iterator)
    except StopIteration:
        error_message = (
            f"error: "
            f"no check strings found with prefix '{config.check_prefix}:'"
        )
        print(error_message, file=sys.stderr)
        sys.stdout.flush()
        exit_handler(2)

    current_scan_base = 0
    # Keeping track of a current scan column is a simplified feature which is
    # not implemented yet:
    # "Without --match-full-lines, LLVM FileCheck allows multiple checks on a
    # same line #52", https://github.com/stanislaw/FileCheck.py/issues/52
    current_scan_col = 0

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
    # "Getting exit code 141 when reading from stdin with a Python script
    # with “set -o pipefail” set"
    # https://stackoverflow.com/questions/59436858/getting-exit-code-141-when-reading-from-stdin-with-a-python-script-with-set-o/59436997?noredirect=1#comment105058533_59436997
    # Also: Forcing the stdin to be UTF-8
    # Python 3: How to specify stdin encoding
    # https://stackoverflow.com/a/16549381/598057
    input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    input_lines = input_stream.readlines()
    stdin_input_iter = enumerate(input_lines)

    try:
        line_idx, line = next(stdin_input_iter)
    except StopIteration:
        print("CHECK: FileCheck error: '-' is empty.")
        print(f"FileCheck command line: {check_file_path}")
        exit_handler(2)

    current_not_checks = []
    try:
        failed_check = None
        failed_implicit_check = None

        while True:
            line = line.rstrip("\n\r")

            unstripped_line = line

            if not config.strict_whitespace:
                line = canonicalize_whitespace(line)
                if config.match_full_lines:
                    line = line.strip(" ")

            while True:
                if not failed_check:
                    for current_not_check in current_not_checks:
                        check_result = check_line(
                            line, current_not_check, config.match_full_lines
                        )
                        if check_result == CheckResult.CHECK_NOT_MATCH:
                            failed_check = FailedCheck(
                                current_not_check, line_idx
                            )
                            break

                if not failed_implicit_check:
                    for check_not_check in implicit_check_not_checks:
                        if implicit_check_line(
                            check_not_check, strict_mode, unstripped_line
                        ):
                            failed_implicit_check = FailedImplicitCheckContext(
                                check_not_check, unstripped_line, line_idx
                            )
                            break

                check_result = check_line(
                    line, current_check, config.match_full_lines
                )

                if check_result == CheckResult.FAIL_FATAL:
                    failed_check = FailedCheck(current_check, line_idx)
                    raise CheckFailedException(failed_check)

                if check_result == CheckResult.PASS:
                    if failed_implicit_check:
                        raise ImplicitCheckNotFailedException(
                            failed_implicit_check
                        )

                    if failed_check:
                        raise CheckFailedException(failed_check)

                    current_not_checks.clear()
                    current_scan_col = len(line)

                    try:
                        current_check = next(check_iterator)
                    except StopIteration:
                        if len(implicit_check_not_checks) == 0:
                            exit_handler(0)

                        for line_idx, line in stdin_input_iter:
                            for check_not_check in implicit_check_not_checks:
                                if implicit_check_line(
                                    check_not_check, strict_mode, line
                                ):
                                    failed_implicit_check = (
                                        FailedImplicitCheckContext(
                                            check_not_check, line, line_idx
                                        )
                                    )
                                    raise ImplicitCheckNotFailedException(
                                        failed_implicit_check
                                    ) from None

                        exit_handler(0)

                    try:
                        line_idx, line = next(stdin_input_iter)
                        current_scan_base = line_idx
                        current_scan_col = 0
                        break
                    except StopIteration:
                        raise InputFinishedException from None

                elif check_result == CheckResult.CHECK_NOT_MATCH:
                    failed_check = FailedCheck(current_check, line_idx)
                    try:
                        current_not_checks.append(current_check)
                        current_check = next(check_iterator)
                        continue
                    except StopIteration:
                        raise CheckFailedException(failed_check) from None

                elif check_result == CheckResult.CHECK_NOT_WITHOUT_MATCH:
                    if failed_check:
                        raise CheckFailedException(failed_check)

                    try:
                        current_not_checks.append(current_check)
                        current_check = next(check_iterator)
                        continue
                    except StopIteration:
                        raise CheckNOTIsLastException from None

                elif check_result == CheckResult.FAIL_SKIP_LINE:
                    try:
                        line_idx, line = next(stdin_input_iter)
                        break
                    except StopIteration:
                        failed_check = FailedCheck(current_check, line_idx)
                        raise CheckFailedException(failed_check) from None

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
                # No checks which are still actual have been found.
                # Declare success.
                exit_handler(0)

            current_check = still_actual_check
            current_check_line_idx = line_idx
    except CheckNOTIsLastException:
        # Here we catch the case when the last check is known to be CHECK-NOT.
        # We have to iterate over the remaining input lines and check them all
        # against this last check.
        try:
            while True:
                line_idx, line = next(stdin_input_iter)

                for not_check in current_not_checks:
                    if (
                        check_line(line, not_check, config.match_full_lines)
                        == CheckResult.CHECK_NOT_MATCH
                    ):
                        current_check_line_idx = line_idx
                        failed_check = FailedCheck(not_check, line_idx)
                        raise CheckFailedException(failed_check) from None

        except CheckFailedException as check_failed_exception:
            current_check = check_failed_exception.failed_check.check
            current_check_line_idx = (
                check_failed_exception.failed_check.line_idx
            )

        except StopIteration:
            exit_handler(0)

    except CheckFailedException as check_failed_exception:
        current_check = check_failed_exception.failed_check.check
        current_check_line_idx = check_failed_exception.failed_check.line_idx

    except ImplicitCheckNotFailedException as implicit_check_not_exception:
        context = implicit_check_not_exception.failed_check_context
        failed_check = context.check
        failed_line_num = context.line_idx + 1

        failed_column_idx = context.line.find(failed_check.check)
        assert failed_column_idx != -1

        failed_column_num = failed_column_idx + 1

        print(
            "command line:1:22: error: CHECK-NOT: excluded string found "
            "in input"
        )
        print(f"-implicit-check-not='{failed_check.original_check}'")
        print("                     ^")
        print(
            f"<stdin>:{failed_line_num}:{failed_column_num}: note: found here"
        )
        print(context.line)
        print(
            "^".rjust(failed_column_idx + 1, " ").ljust(
                len(failed_check.check) + failed_column_idx, "~"
            )
        )
        exit_handler(1)

    # CHECK-EMPTY is special: if there is no output anymore and this check is
    # the 1) current and 2) the last one we want to declare success.
    # Otherwise we switch to a next check, make it current and go to do error
    # reporting below.
    if (
        current_check.check_type == CheckType.CHECK_EMPTY
        and check_result == CheckResult.PASS
    ):
        try:
            current_check = next(check_iterator)
            input_lines.append("")
            current_scan_base += 1
            current_scan_col = 0
        except StopIteration:
            exit_handler(0)

    # Error reporting part. By now we know that we have failed and we just want
    # to report a check that has failed.

    if current_check.check_type == CheckType.CHECK_EMPTY:
        last_read_line = input_lines[current_scan_base].rstrip()
        print(
            f"{check_file_path}:"
            f"{current_check.check_line_idx + 1}:"
            f"{len(current_check.source_line) + 1}: "
            "error: CHECK-EMPTY: expected string not found in input"
        )
        print(current_check.source_line)
        print("^".rjust(len(current_check.source_line) + 1))
        print(f"<stdin>:{current_scan_base + 1}:{1}: note: scanning from here")
        print(last_read_line)
        print("^")

        exit_handler(1)

    if current_check.check_type == CheckType.CHECK:
        assert current_scan_base < len(input_lines)

        # FileCheck prefers to show non-empty lines when printing
        # "Scanning from here" so we are skipping through empty lines if any.
        last_read_line = input_lines[current_scan_base].rstrip()
        while last_read_line == "" and current_scan_base < (
            len(input_lines) - 1
        ):
            current_scan_base += 1
            last_read_line = input_lines[current_scan_base].rstrip()

        if current_check.match_type in (MatchType.SUBSTRING, MatchType.REGEX):
            print(
                f"{check_file_path}:"
                f"{current_check.check_line_idx + 1}:"
                f"{current_check.start_index + 1}: "
                f"error: {config.check_prefix}: "
                f"expected string not found in input"
            )

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))

            print(
                f"<stdin>:{current_scan_base + 1}:{current_scan_col + 1}: "
                f"note: scanning from here"
            )
            print(last_read_line)
            print("^".rjust(current_scan_col + 1))

            # This is rather weird but it looks like with the REGEX case, the
            # FileCheck C++ only prints possible intended matches starting from
            # the line next to the current_scan_base (and only when such line
            # exists!).
            # TODO: this needs more real-world input.

            if current_scan_col != 0:
                current_scan_base += 1

            if current_check.match_type == MatchType.SUBSTRING or (
                current_check.match_type == MatchType.REGEX
                and current_scan_base < (len(input_lines) - 1)
            ):
                candidate_line = None
                candidate_line_idx = None
                current_best_ratio = 0
                for read_line_idx, read_line in enumerate(
                    input_lines[current_scan_base:]
                ):
                    similar_ratio = similar(read_line, current_check.expression)
                    if current_best_ratio < similar_ratio:
                        candidate_line = read_line.rstrip()
                        candidate_line_idx = current_scan_base + read_line_idx
                        current_best_ratio = similar_ratio
                if candidate_line:
                    caret_pos = len(candidate_line) // 2 + 1
                    print(
                        f"<stdin>:{candidate_line_idx + 1}:{caret_pos}: "
                        f"note: possible intended match here"
                    )
                    print(candidate_line)
                    print("^".rjust(caret_pos, " "))

            exit_handler(1)

    if current_check.check_type == CheckType.CHECK_NOT:
        if current_check.match_type in (MatchType.SUBSTRING, MatchType.REGEX):
            assert current_check_line_idx is not None
            last_read_line = input_lines[current_check_line_idx].rstrip()

            if not config.strict_whitespace:
                last_read_line = re.sub("\\s+", " ", last_read_line).strip()

            print(
                f"{check_file_path}:"
                f"{current_check.check_line_idx + 1}:"
                f"{current_check.start_index + 1}: "
                f"error: CHECK-NOT: excluded string found in input"
            )

            print(current_check.source_line.rstrip())
            print("^".rjust(current_check.start_index + 1))
            print(f"<stdin>:{current_check_line_idx + 1}:{1}: note: found here")
            print(last_read_line)

            if current_check.match_type == MatchType.SUBSTRING:
                match_pos = last_read_line.find(current_check.expression)
                assert match_pos != -1

                # TODO: check on lines which start with spaces
                highlight_line = "^".rjust(match_pos, " ")
                print(highlight_line.ljust(len(current_check.expression), "~"))
            else:
                print("^".ljust(len(last_read_line), "~"))

            exit_handler(1)

        assert 0, "Not implemented"

    if current_check.check_type == CheckType.CHECK_NEXT:
        last_read_line = input_lines[current_scan_base].rstrip()

        if current_check.match_type in (MatchType.SUBSTRING, MatchType.REGEX):
            matching_line_idx = -1
            for line_idx, line in enumerate(input_lines[current_scan_base:]):
                if current_check.expression in line:
                    matching_line_idx = current_scan_base + line_idx

            if matching_line_idx == -1:
                print(
                    f"{check_file_path}:"
                    f"{current_check.check_line_idx + 1}:"
                    f"{current_check.start_index + 1}: "
                    f"error: CHECK-NEXT: expected string not found in input"
                )

                print(current_check.source_line.rstrip())
                print("^".rjust(current_check.start_index + 1))
                print(
                    f"<stdin>:{current_scan_base + 1}:{1}: "
                    "note: scanning from here"
                )
                print(last_read_line)
                print("^")

                exit_handler(1)
            else:
                if current_scan_base > 0:
                    print(
                        f"{check_file_path}:"
                        f"{current_check.check_line_idx + 1}:"
                        f"{current_check.start_index + 1}: "
                        "error: CHECK-NEXT: is not on the line after "
                        "the previous match"
                    )
                    print(current_check.source_line.rstrip())
                    print("^".rjust(current_check.start_index + 1))

                    matching_line = input_lines[matching_line_idx].rstrip()
                    print(
                        f"<stdin>:{matching_line_idx + 1}:1: "
                        "note: 'next' match was here"
                    )
                    print(matching_line)
                    print("^")

                    previous_matched_line = input_lines[
                        current_scan_base - 1
                    ].rstrip()
                    print(
                        f"<stdin>:{current_scan_base}:"
                        f"{len(previous_matched_line) + 1}: "
                        f"note: previous match ended here"
                    )
                    print(previous_matched_line)
                    print("^".rjust(len(previous_matched_line) + 1))
                    print(
                        f"<stdin>:{current_scan_base + 1}:{1}: "
                        f"note: non-matching line after previous match is here"
                    )
                    print(last_read_line)
                    print("^")

                    exit_handler(1)
                else:
                    check_expression_idx = current_check.source_line.find(
                        current_check.check_keyword
                    )
                    print(
                        f"{check_file_path}:"
                        f"{current_check.check_line_idx + 1}:"
                        f"{check_expression_idx + 1}: "
                        f"error: found 'CHECK-NEXT' without "
                        f"previous 'CHECK: line"
                    )
                    print(current_check.source_line.rstrip())
                    print("^".rjust(check_expression_idx + 1))

                    exit_handler(2)

        raise NotImplementedError()


if __name__ == "__main__":
    main()
