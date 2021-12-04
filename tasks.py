import os
import platform
import re
from typing import Optional

import invoke
from invoke import task

FILECHECK_LLVM_8_EXEC = 'FileCheck-8.0.1'
FILECHECK_LLVM_9_EXEC = 'FileCheck-9.0.1'


def one_line_command(string):
    return re.sub("\\s+", " ", string).strip()


def run_invoke_cmd(context, cmd) -> invoke.runners.Result:
    return context.run(
        cmd, env=None, hide=False, warn=False, pty=False, echo=True
    )


def get_os_filename_string():
    if platform.system() == 'Windows':
        return "Windows"
    if platform.system() == 'Darwin':
        return "macOS"
    if platform.system() == 'Linux':
        return "Linux"
    assert 0, "error: FileCheck.py could not detect OS"


def get_filecheck_llvm_path(filecheck_exec):
    cwd = os.getcwd()
    os_string = get_os_filename_string()

    template = '\\"{cwd}/tests/integration/tools/FileCheck/{filecheck_exec}-{os_string}\\"'
    return template.format(
        cwd=cwd, filecheck_exec=filecheck_exec, os_string=os_string
    )


def get_filecheck_py_exec():
    cwd = os.getcwd()
    return 'python \\"{cwd}/filecheck/FileCheck.py\\"'.format(cwd=cwd)


def run_lit_tests(
    c, filecheck_exec, filecheck_tester_exec, focus: Optional[str], llvm_only
):
    assert c
    assert filecheck_exec
    assert llvm_only is not None

    cwd = os.getcwd()

    llvm_only_value = "1" if llvm_only else ""
    focus_or_none = f"--filter {focus}" if focus else ""

    command = one_line_command("""
        lit
        --param REAL_ONLY={llvm_only_value}
        --param FILECHECK_EXEC="{filecheck_exec}"
        --param FILECHECK_TESTER_EXEC="{filecheck_tester_exec}"
        -v
        {focus_or_none}
        {cwd}/tests/integration
    """).format(cwd=cwd,
                filecheck_exec=filecheck_exec,
                filecheck_tester_exec=filecheck_tester_exec,
                focus_or_none=focus_or_none,
                llvm_only_value=llvm_only_value)

    run_invoke_cmd(c, command)


@task
def test_filecheck_llvm(c, focus=None):
    # filecheck_llvm_8_exec = get_filecheck_llvm_path(FILECHECK_LLVM_8_EXEC)
    filecheck_llvm_9_exec = get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC)
    filecheck_tester_exec = get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC)

    # run_lit_tests(c, filecheck_llvm_8_exec, filecheck_tester_exec, True)
    run_lit_tests(c, filecheck_llvm_9_exec, filecheck_tester_exec, focus, True)


@task
def test_filecheck_py_using_file_check_llvm_tester(c, focus=None):
    filecheck_exec = get_filecheck_py_exec()
    filecheck_tester_exec = get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC)

    run_lit_tests(c, filecheck_exec, filecheck_tester_exec, focus, False)


@task
def test_filecheck_py_using_filecheck_py_tester(c, focus=None):
    filecheck_exec = get_filecheck_py_exec()
    filecheck_tester_exec = filecheck_exec

    run_lit_tests(c, filecheck_exec, filecheck_tester_exec, focus, False)


@task
def test(c, focus=None):
    test_filecheck_llvm(c, focus)
    test_filecheck_py_using_file_check_llvm_tester(c, focus)


@task
def clean(c):
    find_command = one_line_command("""
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
    """)

    find_result = run_invoke_cmd(c, find_command)
    find_result_stdout = find_result.stdout.strip()

    echo_command = one_line_command(
        """echo {find_result} | xargs rm -rfv""".format(find_result=find_result_stdout)
    )
    run_invoke_cmd(c, echo_command)


@task
def docs_sphinx(c, open=False):
    run_invoke_cmd(c, one_line_command("""
        cd docs && make html SPHINXOPTS="-W --keep-going -n"
    """))
    if open:
        run_invoke_cmd(
            c, one_line_command("""
                open docs/_build/html/index.html
            """)
        )


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(c, github_token):
    command = one_line_command("""
        CHANGELOG_GITHUB_TOKEN={github_token}
        github_changelog_generator
        --user mull-project
        --project FileCheck.py
    """).format(github_token=github_token)
    run_invoke_cmd(c, command)
