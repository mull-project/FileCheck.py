import os
import platform
import re
from typing import Optional

import invoke
from invoke import task

FILECHECK_LLVM_8_EXEC = "FileCheck-8.0.1"
FILECHECK_LLVM_9_EXEC = "FileCheck-9.0.1"


def one_line_command(string):
    return re.sub("\\s+", " ", string).strip()


def run_invoke_cmd(context, cmd) -> invoke.runners.Result:
    return context.run(
        cmd, env=None, hide=False, warn=False, pty=False, echo=True
    )


def get_os_filename_string():
    if platform.system() == "Windows":
        return "Windows"
    if platform.system() == "Darwin":
        return "macOS"
    if platform.system() == "Linux":
        return "Linux"
    assert 0, "error: FileCheck.py could not detect OS"


def get_filecheck_llvm_path(filecheck_exec):
    cwd = os.getcwd()
    os_string = get_os_filename_string()

    template = f'\\"{cwd}/tests/integration/tools/FileCheck/{filecheck_exec}-{os_string}\\"'
    return template


def get_filecheck_py_exec():
    cwd = os.getcwd()
    return f'python \\"{cwd}/filecheck/FileCheck.py\\"'


def run_lit_tests(
    context,
    filecheck_exec,
    filecheck_tester_exec,
    focus: Optional[str],
    llvm_only,
):
    assert context
    assert filecheck_exec
    assert llvm_only is not None

    cwd = os.getcwd()

    llvm_only_value = "1" if llvm_only else ""
    focus_or_none = f"--filter {focus}" if focus else ""

    command = one_line_command(
        f"""
            lit
            --param REAL_ONLY={llvm_only_value}
            --param FILECHECK_EXEC="{filecheck_exec}"
            --param FILECHECK_TESTER_EXEC="{filecheck_tester_exec}"
            -v
            {focus_or_none}
            {cwd}/tests/integration
        """
    )

    run_invoke_cmd(context, command)


@task
def lint_black_diff(context):
    command = one_line_command(
        """
        black . --color 2>&1
        """
    )
    result = run_invoke_cmd(context, command)

    # black always exits with 0, so we handle the output.
    if "reformatted" in result.stdout:
        print("invoke: black found issues")
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task
def lint_flake8(context):
    command = one_line_command(
        """
        flake8 filecheck/ --statistics --max-line-length 80 --show-source
        """
    )
    run_invoke_cmd(context, command)


@task
def lint_pylint(context):
    command = one_line_command(
        """
        pylint
          --rcfile=.pylint.ini
          --disable=all
          --fail-under=10.0
          --enable=E1101,R0201,R0902,R0913,R1701,R1705,R1710,R1714,R1719,R1725,C0103,C0209,C0303,C0411,C1801,W0703,W0231,W0235,W0612,W0613,W0640,W0707,W1514
          filecheck/ tasks.py
        &&
        pylint
          --rcfile=.pylint.ini
          --disable=c-extension-no-member
          --exit-zero
          filecheck/ tasks.py
        """  # pylint: disable=line-too-long
    )
    try:
        run_invoke_cmd(context, command)
    except invoke.exceptions.UnexpectedExit as exc:
        # pylink doesn't show an error message when exit code != 0, so we do.
        print(f"invoke: pylint exited with error code {exc.result.exited}")
        raise exc


@task(lint_black_diff, lint_flake8)
def lint(_):
    pass


@task
def test_filecheck_llvm(context, focus=None):
    # filecheck_llvm_8_exec = get_filecheck_llvm_path(FILECHECK_LLVM_8_EXEC)
    filecheck_llvm_9_exec = get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC)
    filecheck_tester_exec = get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC)

    # run_lit_tests(c, filecheck_llvm_8_exec, filecheck_tester_exec, True)
    run_lit_tests(
        context, filecheck_llvm_9_exec, filecheck_tester_exec, focus, True
    )


@task
def test_filecheck_py_using_file_check_llvm_tester(context, focus=None):
    filecheck_exec = get_filecheck_py_exec()
    filecheck_tester_exec = get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC)

    run_lit_tests(context, filecheck_exec, filecheck_tester_exec, focus, False)


@task
def test_filecheck_py_using_filecheck_py_tester(context, focus=None):
    filecheck_exec = get_filecheck_py_exec()
    filecheck_tester_exec = filecheck_exec

    run_lit_tests(context, filecheck_exec, filecheck_tester_exec, focus, False)


@task(lint)
def test(context, focus=None):
    test_filecheck_llvm(context, focus)
    test_filecheck_py_using_file_check_llvm_tester(context, focus)


@task
def clean(context):
    find_command = one_line_command(
        """
        find
            .
            -type f \\(
                -name '*.script'
            \\)
            -or -type d \\(
                -name '*.dSYM' -or
                -name 'Sandbox' -or
                -name 'Output' -or
                -name 'output'
            \\)
            -not -path "**Expected**"
            -not -path "**Input**"
    """
    )

    find_result = run_invoke_cmd(context, find_command)
    find_result_stdout = find_result.stdout.strip()

    echo_command = one_line_command(
        f"""echo {find_result_stdout} | xargs rm -rfv"""
    )
    run_invoke_cmd(context, echo_command)


@task
def docs_sphinx(context, open_doc=False):
    run_invoke_cmd(
        context,
        one_line_command(
            """
        cd docs && make html SPHINXOPTS="-W --keep-going -n"
    """
        ),
    )
    if open_doc:
        run_invoke_cmd(
            context,
            one_line_command(
                """
                open docs/_build/html/index.html
            """
            ),
        )


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(context, github_token):
    command = one_line_command(
        f"""
            CHANGELOG_GITHUB_TOKEN={github_token}
            github_changelog_generator
            --user mull-project
            --project FileCheck.py
        """
    )
    run_invoke_cmd(context, command)
