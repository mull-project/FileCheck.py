# FileCheck.py

Attempt to reimplement LLVM's FileCheck using Python.

![](https://github.com/mull-project/FileCheck.py/workflows/FileCheck.py%20on%20macOS/badge.svg)
![](https://github.com/mull-project/FileCheck.py/workflows/FileCheck.py%20on%20Linux/badge.svg)
![](https://github.com/mull-project/FileCheck.py/workflows/FileCheck.py%20on%20Windows/badge.svg)

## Background

Many software projects could benefit from a suite of LLVM LIT integration tests.
The problem is that you have to build `FileCheck` from LLVM sources
which is not a trivial task for 1) people who are not familiar with the LLVM
infrastructure and 2) Python-based projects that would prefer to not have
to build anything from LLVM's source code in their CI process.

The option of having pre-compiled binaries is a workaround, but we don't like to
keep third-party binary artifacts in source code.

## Documentation

Documentation is hosted on Read the Docs:

[FileCheck.py documentation](https://filecheck.readthedocs.io/en/stable/index.html)

## Copyright

Copyright (c) 2019-2023 Stanislav Pankevich s.pankevich@gmail.com. See
LICENSE for
details.

