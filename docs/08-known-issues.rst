Known issues
============

FileCheck always prints a full path to itself
---------------------------------------------

LLVM FileCheck always prints its own path to the output so the first line is
always the path. This always happens regardless of a test outcome: success or
failure. FileCheck.py follows LLVM FileCheck and does the same, even though
there seems to be no reason to do that every time.

Unintuitive behavior of CHECK-NOT
---------------------------------

A failing CHECK has a higher precedence than a failing CHECK-NOT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A failing `CHECK` has a higher precedence than a failing `CHECK-NOT` even if
`CHECK-NOT` appears first in the check file. If this happens, the output is
related to the failing `CHECK`, not the failing `CHECK-NOT`.

Input:

.. code-block:: text

   String1
   Stringggg2

Check file:

.. code-block:: text

   ; CHECK-NOT:String1
   ; CHECK:String2

Result:

.. code-block:: text

   /Users/Stanislaw/.pyenv/shims/filecheck
   filecheck.check:2:9: error: CHECK: expected string not found in input
   ; CHECK:String2
           ^
   <stdin>:1:1: note: scanning from here
   String1
   ^
