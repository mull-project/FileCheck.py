What is FileCheck.py
====================

**FileCheck.py** is a Python port of the **LLVM's FileCheck**, "flexible
pattern matching file verifier" [1_].

LLVM's FileCheck is a command-line tool written in C++ which
is developed and maintained as part of LLVM source code [2_].

FileCheck is most often used in a combination with another tool called **LIT
(LLVM Integrated Tester)** [3_]. LIT is a test runner that runs commands
from the test files, FileCheck is used as a test matcher tool that checks output
of the commands run by LIT.

Why Python port?
----------------

There are software projects that would benefit from having a suite of LLVM LIT
integration tests. Mull mutation testing system is one example [4_].

The problem is that you have to build FileCheck from LLVM sources which is not a trivial task for 1) people who are not aware with the LLVM infrastructure and 2) Python-based projects that would prefer to not have to build anything from LLVM sources in their CI process.

The option of having pre-compiled binaries is a workaround, but it is not always
possible to keep third-party binary artifacts in source code,
(see https://github.com/doorstop-dev/doorstop/pull/431#issuecomment-549237579).

Simple example
--------------

When writing LIT/FileCheck tests it is common to combine the LIT's ``RUN``
commands and FileCheck's ``CHECK`` assertions in a single file.

Passing test
~~~~~~~~~~~~

Test file ``01-pass.c``:

.. code-block:: c

    /**
    ; RUN: clang %s -o %S/hello-world && %S/hello-world | filecheck %s
    ; CHECK: Hello world
     */

    #include <stdio.h>
    int main() {
      printf("Hello world\n");
      return 0;
    }

Command:

.. code-block:: bash

   $ lit 01-pass.c

Output:

.. code-block:: text

    -- Testing: 1 tests, single process --
    PASS: <unnamed> :: 01-pass.c (1 of 1)
    Testing Time: 0.10s
      Expected Passes    : 1

Failing test
~~~~~~~~~~~~

Test file ``02-fail.c``:

.. code-block:: c

    /**
    ; RUN: clang %s -o %S/hello-world && %S/hello-world | filecheck %s
    ; CHECK: Wrong line
     */

    #include <stdio.h>
    int main() {
      printf("Hello world\n");
      return 0;
    }


Command:

.. code-block:: bash

    $ lit 02-fail.c

Output:

.. code-block:: text

    -- Testing: 1 tests, single process --
    FAIL: <unnamed> :: 02-fail.c (1 of 1)
    Testing Time: 0.11s
    ********************
    Failing Tests (1):
        <unnamed> :: 02-fail.c

      Unexpected Failures: 1

The verbose version:

.. code-block:: bash

    $ lit -v 02-fail.c

Produces more output:

.. code-block:: text

    -- Testing: 1 tests, single process --
    FAIL: <unnamed> :: 02-fail.c (1 of 1)
    ******************** TEST '<unnamed> :: 02-fail.c' FAILED ********************
    02-fail.c:3:10: error: CHECK: expected string not found in input
    ; CHECK: Wrong line
             ^
    <stdin>:1:1: note: scanning from here
    Hello world
    ...
    ********************
    Testing Time: 0.11s
    ********************
    Failing Tests (1):
        <unnamed> :: 02-fail.c

      Unexpected Failures: 1

Links
-----

.. _1:

[1] `FileCheck - Flexible pattern matching file verifier
<https://llvm.org/docs/CommandGuide/FileCheck.html>`_

.. _2:

[2] `llvm/utils/FileCheck/FileCheck.cpp
<https://github.com/llvm/llvm-project/blob/fdde18a7c3e5ae62f458fb83230ec340bf658668/llvm/utils/FileCheck/FileCheck.cpp>`_

.. _3:

[3] `lit - LLVM Integrated Tester
<https://llvm.org/docs/CommandGuide/lit.html>`_

.. _4:

[4] `Mull mutation testing system
<https://github.com/mull-project/mull/pulls>`_
