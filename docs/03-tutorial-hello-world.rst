Tutorial: Hello World
=====================

This tutorial assumes that you have ``filecheck`` installed and have it
available in your PATH:

.. code-block:: bash

   $ filecheck
   /usr/local/bin/filecheck
   <check-file> not specified

FileCheck can be seen as an improved version of ``grep`` that makes automated
testing of the command-line tools easier. FileCheck reads an input and scans it
against a number of checks which can be substring or regex matches. If all check
matches are found, ``FileCheck`` exits with an exit code ``0``. When a check
without a match found, the FileCheck prints an error message and exits with an
exit code ``1``.

The FileCheck program expects a path to a check file and a number of optional
option arguments:

.. code-block:: text

   $ filecheck <check-file> [<options>]

Matching strings
----------------

Create new file ``hello-world.check`` with the following contents:

.. code-block:: text

   ; CHECK: Hello world

Now we can provide a valid input to ``filecheck`` which will match it against
the check file:

.. code-block:: bash

   $ echo "Hello world" | filecheck hello-world.check
   /usr/local/bin/filecheck
   $ echo $?
   0

**Note:** By convention, original LLVM's ``FileCheck`` always prints a full
path to its executable and ``FileCheck.py`` follows this convention.

If we provide an invalid output we will see an error message:

.. code-block:: bash

   $ echo "What is FileCheck" | filecheck hello-world.check
   /usr/local/bin/filecheck
   examples/hello-world.check:1:10: error: CHECK: expected string not found in input
   ; CHECK: Hello world
            ^
   <stdin>:1:1: note: scanning from here
   What is FileCheck
   ^
   $ echo $?
   1

It is as easy as that!

Matching regular expressions
----------------------------

``FileCheck`` also supports regex matching using special ``{{ }}`` syntax:

Create a new file ``hello-world-regex.check`` with the following contents:

.. code-block:: text

   ; CHECK: {{^Hello world$}}

Let's run it with a valid input:

.. code-block:: bash

   echo "Hello world" | filecheck examples/hello-world-regex.check
   /usr/local/bin/filecheck
   $ echo $?
   0

With invalid input:

.. code-block:: bash

   $ echo "Hello world Hello world" | filecheck examples/hello-world-regex.check
   /usr/local/bin/filecheck
   examples/hello-world-regex.check:1:10: error: CHECK: expected string not found in input
   ; CHECK: {{^Hello world$}}
            ^
   <stdin>:1:1: note: scanning from here
   Hello world Hello world
   ^
   $ echo $?
   1

What's next?
------------

`FileCheck` is rarely used alone. The main use case for `FileCheck` is to serve
as an assertion matcher tool when it is used in a combination with the
LLVM LIT Integrated Tester and this is what our next tutorial is about. Don't
stop here and check it out right away: :doc:`04-tutorial-lit-and-filecheck`.
