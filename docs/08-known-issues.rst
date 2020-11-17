Known issues
============

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

   CHECK-NOT:String1
   CHECK:String2

Result:

.. code-block:: text

   /Users/Stanislaw/.pyenv/shims/filecheck
   filecheck.check:2:7: error: CHECK: expected string not found in input
   CHECK:String2
         ^
   <stdin>:1:1: note: scanning from here
   String1
   ^
