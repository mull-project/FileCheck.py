Tutorial: LIT and FileCheck
===========================

This tutorial assumes that you have installed ``lit`` and ``filecheck`` and have
them available in your PATH:

.. code-block:: bash

   $ filecheck
   /usr/local/bin/filecheck
   <check-file> not specified

.. code-block:: bash

   $ lit
   ...
   lit: error: No inputs specified

Minimal example
---------------

When writing LIT/FileCheck tests it is common, but not required, to combine
LIT's ``RUN`` commands and FileCheck's ``CHECK`` assertions in a single file.

Let's create a file ``minimal.itest`` with the following contents

.. code-block:: text

    RUN: echo "Hello world" | filecheck %s
    CHECK: Hello world

LIT expects a config file in a directory from which it is run. Let's create
a minimal one called ``lit.cfg``:

.. code-block:: text

    import lit.formats
    config.test_format = lit.formats.ShTest("0")

Now we can run ``lit``:

.. code-block:: bash

    lit minimal.itest

.. code-block:: bash

    -- Testing: 1 tests, single process --
    PASS: <unnamed> :: test.itest (1 of 1)
    Testing Time: 0.10s
      Expected Passes    : 1

Example: testing output of C program
------------------------------------

Passing test
~~~~~~~~~~~~

Test file ``01-pass.c``:

.. code-block:: c

    /**
    RUN: clang %s -o %S/hello-world && %S/hello-world | filecheck %s
    CHECK: Hello world
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
    RUN: clang %s -o %S/hello-world && %S/hello-world | filecheck %s
    CHECK: Wrong line
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
    02-fail.c:3:8: error: CHECK: expected string not found in input
    CHECK: Wrong line
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
