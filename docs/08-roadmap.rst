.. _roadmap:

Roadmap
=======

2024-07-10 STATUS UPDATE - PROJECT DISCONTINUED
-----------------------------------------------

The project has been discontinued in favor of another project: `antonlydike/filecheck <https://github.com/AntonLydike/filecheck>`_, where the developers are aiming to achieve greater compatibility with the upstream LLVM FileCheck and add more features that this project was lacking.

The filecheck PyPI package has also been transferred to the owner of antonlydike/filecheck.

----

As described in :doc:`01-what-is-filecheck`, FileCheck.py is only a Python port
for LLVM's FileCheck. It is not intended to be a replacement for LLVM's
FileCheck.

FileCheck.py is being tested against Mull mutation testing system. The first
goal is to make FileCheck.py pass on Mull's current integration tests suite that
uses only a very limited subset of FileCheck's features which are as follows:

- Commands (both substring and regex matching):

  - ``CHECK``
  - ``CHECK-NEXT``
  - ``CHECK-NOT``
  - ``CHECK-EMPTY``

- Options:

  - ``--strict-whitespace``
  - ``--match-full-lines``
  - ``--check-prefix``

When the above features are implemented and considered stable, it might be a
good idea to implement full FileCheck's contract and be 100% compatible with the
C++ version.

There is a file in FileCheck.py's repository:
`FileCheck.pdf <https://github.com/stanislaw/FileCheck.py/blob/master/FileCheck.pdf>`_
which has some rough implementation coverage: green color means something is
implemented, yellow color means that the text is not relevant to implementation,
no highlighting means "still to be implemented".

Notes on implementation
-----------------------

The implementation is done against the latest
`FileCheck - Flexible pattern matching file verifier <https://llvm.org/docs/CommandGuide/FileCheck.html>`_
document. The plan is to skip looking into the LLVM's implementation of
FileCheck, unless some very advanced implementation details are encountered.

It a nice programming exercise of implementing something from a spec but we also
want to make FileCheck.py conform to the same contract this is why FileCheck.py
is tested using LIT and LLVM's FileCheck:

- First, the LLVM FileCheck is run against a FileCheck.py test suite based on
  LIT/FileCheck.
- Second, FileCheck.py is run on the same tests to make sure that it has the
  same behavior as the LLVM FileCheck.
