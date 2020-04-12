import os
import platform
import re

from invoke import task

FILECHECK_LLVM_8_EXEC = 'FileCheck-8.0.1'
FILECHECK_LLVM_9_EXEC = 'FileCheck-9.0.1'


def get_os_filename_string():
    if platform.system() == 'Windows':
        return "Windows"
    if platform.system() == 'Darwin':
        return "macOS"
    if platform.system() == 'Linux':
        return "Linux"
    assert 0, "error: FileCheck.py could not detect OS"


def get_filecheck_py_exec():
    cwd = os.getcwd()
    return 'python \\"{cwd}/filecheck/FileCheck.py\\"'.format(cwd=cwd)


def get_filecheck_tester_exec():
    cwd = os.getcwd()
    os_string = get_os_filename_string()

    template = '\\"{cwd}/tests/integration/tools/FileCheck/FileCheck-9.0.1-{os_string}\\"'
    return template.format(cwd=cwd, os_string=os_string)


def get_filecheck_llvm_path(filecheck_exec):
    cwd = os.getcwd()
    os_string = get_os_filename_string()

    template = '\\"{cwd}/tests/integration/tools/FileCheck/{filecheck_exec}-{os_string}\\"'
    return template.format(
        cwd=cwd, filecheck_exec=filecheck_exec, os_string=os_string
    )


def formatted_command(string):
    return re.sub('\\s+', ' ', string).strip()


def run_lit_tests(c, filecheck_exec, llvm_only):
    assert c
    assert filecheck_exec
    assert llvm_only is not None

    cwd = os.getcwd()

    llvm_only_value = "1" if llvm_only else ""
    filecheck_tester_exec = get_filecheck_tester_exec()

    command = formatted_command("""
        lit
        --param REAL_ONLY={llvm_only_value}
        --param FILECHECK_EXEC="{filecheck_exec}"
        --param FILECHECK_TESTER_EXEC="{filecheck_tester_exec}"
        -v
        {cwd}/tests/integration
    """).format(cwd=cwd,
                filecheck_exec=filecheck_exec,
                filecheck_tester_exec=filecheck_tester_exec,
                llvm_only_value=llvm_only_value)

    print(command)
    c.run("{}".format(command))


@task
def test(c):
    run_lit_tests(c, get_filecheck_llvm_path(FILECHECK_LLVM_8_EXEC), True)
    run_lit_tests(c, get_filecheck_llvm_path(FILECHECK_LLVM_9_EXEC), True)
    run_lit_tests(c, get_filecheck_py_exec(), False)

@task
def clean(c):
    find_command = formatted_command("""
        find
            .
            -type f \\(
                -name '*.script'
            \\)
            -or -type d \\(
                -name '*.dSYM' -or
                -name 'Sandbox' -or
                -name 'Output'
            \\)
            -not -path "**Expected**"
            -not -path "**Input**"
    """)

    find_result = c.run("{}".format(find_command))
    find_result_stdout = find_result.stdout.strip()

    echo_command = formatted_command(
        """echo {find_result} | xargs rm -rfv""".format(find_result=find_result_stdout)
    )

    c.run("{}".format(echo_command))


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(c, github_token):
    command = formatted_command("""
        CHANGELOG_GITHUB_TOKEN={github_token}
        github_changelog_generator
        --user stanislaw
        --project FileCheck.py
    """).format(github_token=github_token)
    c.run("{}".format(command))
