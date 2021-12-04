Extra features from LLVM FileCheck
==================================

Line number expression
----------------------

It is often useful to check for a specific line number in your regular
expression, relative to its location in the file. Hard-coding that number can
make the test fragile -- rearranging, adding, or deleting lines requires
changing the expression. To solve this, FileCheck supports a variable for the
current line number, ``[[# @LINE ]]``, as well as simple offsets from this
variable, e.g. ``[[# @LINE + 4 ]]`` or ``[[# @LINE - 2 ]]``.

Example:

.. code-block:: c

    /**
    RUN: gcc "%s" -o %S/line && %S/line | filecheck %s
    */

    #include <stdio.h>
    int main() {
      // CHECK: Hello from line [[# @LINE + 1 ]]
      printf("Hello from line %d\n", __LINE__);
      return 0;
    }

See also
`LLVM FileCheck documentation for this feature
<https://llvm.org/docs/CommandGuide/FileCheck.html#filecheck-pseudo-numeric-variables>`_.
