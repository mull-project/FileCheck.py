Tutorial: LLVM LIT and FileCheck
================================

This tutorial assumes that you have installed ``filecheck`` and have it
available in your PATH:

.. code-block:: bash

   $ filecheck
   /usr/local/bin/filecheck
   <check-file> not specified

The FileCheck program expects a path to a check file and a number:

.. code-block:: text

   filecheck <check-file> [<options>]

Create a new file ``hello-world.check`` with the following contents:

.. code-block:: text

   ; CHECK: Hello world

.. code-block:: bash

   echo "Hello world" | filecheck hello-world.check
   /usr/local/bin/FileCheck

