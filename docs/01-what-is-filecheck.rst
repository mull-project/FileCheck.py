What is FileCheck.py
====================

**FileCheck.py** is a Python port of **LLVM's FileCheck**, "flexible
pattern matching file verifier" [1_].

LLVM's FileCheck is a command-line tool written in C++ which
is developed and maintained as part of LLVM source code [2_].

FileCheck is most often used in a combination with another tool called **LIT
(LLVM Integrated Tester)** [3_]. LIT is a test runner that runs commands
from the test files, FileCheck is used as a test matcher tool that checks output
of the commands run by LIT.

Why Python port?
----------------

There are software projects that would benefit from having a suite of LIT-based
integration tests. Mull mutation testing system is one example [4_].

The problem is that you have to build FileCheck from LLVM sources which is not a trivial task for 1) people who are not familiar with the LLVM infrastructure and
2) Python-based projects which would prefer to not depend on anything C or
C++-related including building dependencies from LLVM sources.

The option of having pre-compiled binaries is a workaround, but it is not always
possible to keep third-party binary artifacts in source code
(see
https://github.com/doorstop-dev/doorstop/pull/431#issuecomment-549237579).

**Note:** FileCheck.py is not intended to be a replacement for LLVM's FileCheck
in any way. See :ref:`roadmap`.

What's next?
------------

If you are new to FileCheck and integration testing using LIT, we recommend you
to read the tutorials: :doc:`03-tutorial-hello-world` and
:doc:`04-tutorial-lit-and-filecheck`.

If you know how FileCheck and LIT work, you can check out the status of the port
on the :ref:`roadmap` page.

Links
-----

.. _1:

[1] `FileCheck - Flexible pattern matching file verifier
<https://llvm.org/docs/CommandGuide/FileCheck.html>`_

.. _2:

[2] `llvm/utils/FileCheck/FileCheck.cpp
<https://github.com/llvm/llvm-project/blob/fdde18a7c3e5ae62f458fb83230ec340bf658668/llvm/utils/FileCheck/FileCheck.cpp>`_

.. _3:

[3] `lit - LLVM Integrated Tester
<https://llvm.org/docs/CommandGuide/lit.html>`_

.. _4:

[4] `Mull mutation testing system
<https://github.com/mull-project/mull/pulls>`_
