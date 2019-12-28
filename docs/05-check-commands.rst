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

``CHECK`` command simply means something has to be in input given to FileCheck.

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

    echo -e "String1" | filecheck CHECK.check
    /Users/Stanislaw/.pyenv/versions/3.5.0/bin/filecheck
    CHECK.check:2:8: error: CHECK: expected string not found in input
    CHECK: String2
           ^
    <stdin>:1:8: note: scanning from here
    String1
           ^

CHECK-NOT
---------

...

CHECK-NEXT
----------

...

CHECK-EMPTY
-----------

...
