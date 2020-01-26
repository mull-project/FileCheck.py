Check commands
==============

If you are new to FileCheck, please make sure you have read the tutorials:
:doc:`03-tutorial-hello-world` and :doc:`04-tutorial-lit-and-filecheck` because
they show how FileCheck is used: standalone and in combination with LIT.

For all of the examples below, please note:

- ``.check`` extension is chosen arbitrarily. FileCheck can work with any file
  names.
- When ``echo`` is used with the ``-e`` flag, the ``\n`` symbols are
  treated as newline symbols. We use it to simulate multiline input for
  FileCheck.

CHECK
-----

``CHECK`` command means that a given string or a regular expression must be
present in input provided to FileCheck.

Create a new file ``CHECK.check`` with the following contents:

.. code-block:: text

    CHECK: String1
    CHECK: String2
    CHECK: String3

Valid input results in the exit code ``0`` that indicates success:

.. code-block:: bash

    echo -e "String1\nString2\nString3" | filecheck CHECK.check
    /Users/Stanislaw/.pyenv/versions/3.5.0/bin/filecheck

Invalid input results in the exit code ``1`` and error message:

.. code-block:: bash

    echo "String1" | filecheck CHECK.check
    /Users/Stanislaw/.pyenv/versions/3.5.0/bin/filecheck
    CHECK.check:2:8: error: CHECK: expected string not found in input
    CHECK: String2
           ^
    <stdin>:1:8: note: scanning from here
    String1
           ^

Order of matching
~~~~~~~~~~~~~~~~~

CHECK commands are checked one after another. If a CHECK string is not found in
output, FileCheck exits with error immediately.

Create a new file ``order-of-matching.check`` with the following contents:

.. code-block:: text

    CHECK: String1
    CHECK: String2
    CHECK: String3

And run with invalid input:

.. code-block:: text

    echo "String1" | filecheck order-of-matching.check
    ...
    order-of-matching.check:2:8: error: CHECK: expected string not found in input
    CHECK: String2
           ^
    <stdin>:1:8: note: scanning from here
    String1
           ^

CHECK-NOT
---------

``CHECK-NOT`` is the opposite of ``CHECK``: a given string or a regular
expression must not be present in input provided to FileCheck.

Example
~~~~~~~

``CHECK-NOT.check`` file:

.. code-block:: text

    CHECK-NOT: String1
    CHECK-NOT: String2
    CHECK-NOT: String3

.. code-block:: bash

    $ echo "String3" | filecheck CHECK-NOT.check
    filecheck
    CHECK-NOT.check:3:12: error: CHECK-NOT: excluded string found in input
    CHECK-NOT: String3
               ^
    <stdin>:1:1: note: found here
    String3
    ^~~~~~~

CHECK-NEXT
----------

``CHECK-NEXT`` command means that a given string or a regular expression must be
present in input provided to FileCheck. Additionally, there must be another
check right before ``CHECK-NEXT``, that has passed on the input line just before
the current input line. ``CHECK-NEXT`` cannot be the first check in the check
file.

Check file ``CHECK-NEXT.check``:

.. code-block:: text

    CHECK: String1
    CHECK-NEXT: String2

.. code-block:: bash

    $ echo -e "String1\nString2" | filecheck CHECK-NEXT.check
    ...filecheck
    $ echo $?
    0

.. code-block:: bash

    $ echo -e "String1\nfoo\nString2" | filecheck CHECK-NEXT.check
    ...filecheck
    CHECK-NEXT.check:2:13: error: CHECK-NEXT: is not on the line after the previous match
    CHECK-NEXT: String2
                ^
    <stdin>:3:1: note: 'next' match was here
    String2
    ^
    <stdin>:1:8: note: previous match ended here
    String1
           ^
    <stdin>:2:1: note: non-matching line after previous match is here
    foo
    ^

CHECK-EMPTY
-----------

``CHECK-EMPTY`` command is used to match empty lines.

Consider the following check file:

.. code-block:: text

    CHECK: String1
    CHECK-EMPTY:
    CHECK: String2

In the following example, there is an empty line so the test will pass:

.. code-block:: bash

    echo -e "String1\n\nString2" | filecheck CHECK-EMPTY.check
    ...filecheck
    $ echo $?
    0

If the empty line is removed, the test will fail:

    echo -e "String1\nString2" | filecheck CHECK-EMPTY.check
    ...filecheck
    ...CHECK-EMPTY.check:2:13: error: CHECK-EMPTY: expected string not found in input
    CHECK-EMPTY:
                ^
    <stdin>:2:1: note: scanning from here
    String2
    ^
    $ echo $?
    1
