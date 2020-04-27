Options
=======

--strict-whitespace
-------------------

When the ``--strict-whitespace``  option is not provided, FileCheck ignores
differences between spaces and tabs. Additionally multiple spaces are ignored
and treated as one space.

Example
~~~~~~~

The following check file ``without--strict-whitespace.check``:

.. code-block:: text

    CHECK: String1   String2           String3

will pass on any of the following inputs:

.. code-block:: bash

    printf "String1 String2 String3" | filecheck without--strict-whitespace.check
    printf "String1  String2          String3" | filecheck without--strict-whitespace.check
    printf "   String1\tString2\t\t\tString3 " | filecheck without--strict-whitespace.check

Adding ``--strict-whitespace`` disables this behavior.

--match-full-lines
------------------

When the ``--match-full-lines``  option is not provided, FileCheck does not
match full lines.

Example
~~~~~~~

The following check file ``without--match-full-lines.check``:

.. code-block:: text

    CHECK: tring1
    CHECK: ring2
    CHECK: String3

will pass on the following input:

.. code-block:: bash

    printf "String1\nString2\nString3" | filecheck without--match-full-lines.check

The ``--match-full-lines`` disables this behavior.

Strict mode
~~~~~~~~~~~

Additionally, when the ``--strict-whitespace`` option is also provided,
FileCheck does not allow leading and trailing whitespaces.

The following input: ``printf "String1\nString2\nString3"`` will only be matched
with the following check file:

.. code-block:: text

    CHECK:String1
    CHECK:String2
    CHECK:String3

Notice absence of spaces between ``CHECK:`` and the lines.

.. code-block:: bash

    $ printf "String1\nString2\nString3" | filecheck strict-mode.check --strict-whitespace --match-full-lines
    ...filecheck
    $ echo $?
    0

--check-prefix
--------------

The ``--check-prefix`` option allows changing a default match keyword `CHECK`
to an arbitrary keyword. This is useful when you want to test different behavior
in the same file:

.. code-block:: text

    ; RUN: printf "String1" | %FILECHECK_EXEC %s --check-prefix STRING1
    ; RUN: printf "String2" | %FILECHECK_EXEC %s --check-prefix STRING2
    ; STRING1: String1
    ; STRING2: String2

One usual case is testing of how a program behaves when it is run with or
without a specific option.

--implicit-check-not
--------------------

The ``--implicit-check-not`` option adds implicit `CHECK-NOT` check that works
on every input line.

FileCheck.py follows LLVM FileCheck in the following implementation details:

- The implicit checks are substring-matched i.e. their are ``in`` checks, not
``==`` checks.

- The implicit checks are case sensitive, so ``error`` check will not match
``ERROR`` in the input.

- The implicit check has lower priority than the positive `CHECK*` checks,
but it has higher priority than negative `CHECK-NOT` checks.

- To provide multiple implicit checks, duplicate the argument
``--implicit-check-not <your check>`` multiple times.

Example
~~~~~~~

A very useful application of this option is to add implicit
``--implicit-check-not error --implicit-check-not warning`` checks to make sure
that the input never has lines that contain ``error`` or ``warning`` in them.
