Check commands
==============

If you are new to FileCheck, please make sure you have read the tutorials:
:doc:`03-tutorial-hello-world` and :doc:`04-tutorial-lit-and-filecheck` because
they show how FileCheck is used: standalone and in combination with LIT.

For all of the examples below, please note:

- ``.check`` extension is chosen arbitrarily. FileCheck can work with any file
  names.
- FileCheck always prints its own path to the output. This always happens
  regardless of input.
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

...

CHECK-EMPTY
-----------

...
