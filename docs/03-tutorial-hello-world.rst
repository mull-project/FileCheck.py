Tutorial: Hello World
=====================

This tutorial assumes that you have installed ``filecheck`` and have it
available in your PATH:

.. code-block:: bash

   $ filecheck
   /usr/local/bin/filecheck
   <check-file> not specified

The FileCheck program expects the following grammar:

.. code-block:: text

   filecheck <check-file> [<options>]

Create new file ``hello-world.check`` with the following contents:

.. code-block:: text

   ; CHECK: Hello world

.. code-block:: bash

   echo "Hello world" | filecheck hello-world.check
   /usr/local/bin/FileCheck


