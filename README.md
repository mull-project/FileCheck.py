# FileCheck.py

Attempt to reimplement LLVM's FileCheck using Python.

## Background

We know at least two software projects that would benefit from a suite of
LLVM LIT integration tests:

1. [Mull](https://github.com/mull-project/mull)

2. [Doorstop](https://github.com/doorstop-dev/doorstop/pull/431)

The problem is that you have to build `FileCheck` from LLVM sources
which is not a trivial task for 1) people who are not aware with the LLVM
infrastructure and 2) Python-based projects that would prefer to not have
to build anything from LLVM sources in their CI process.

The option of having pre-compiled binaries is a workaround, but we don't like to
keep third-party binary artifacts in source code,
(see https://github.com/doorstop-dev/doorstop/pull/431#issuecomment-549237579).

## Goals

The first goal is to make FileCheck.py pass on Mull's current integration
tests suite which uses only a very limited subset of FileCheck's features which
are as follows:

- Commands (both substring and regex matching):
  - `CHECK`
  - `CHECK-NEXT`
  - `CHECK-NOT`
  - `CHECK-EMPTY`
- Options:
  - `--strict-whitespace`
  - `--match-full-lines`
  - `--check-prefix`

When this is done, it feels like a good idea to implement full FileCheck's
contract and be 100% compatible with the C++ version.

There is a file in this repository: [FileCheck.pdf](FileCheck.pdf) which has
some rough implementation coverage: green color means something is implemented,
yellow color means that the text is not relevant to implementation, no
highlighting means "still to be implemented".

## Notes on implementation

The implementation is done against the latest
[FileCheck - Flexible pattern matching file verifier](https://llvm.org/docs/CommandGuide/FileCheck.html)
document. The plan is to skip looking into the LLVM's implementation of
FileCheck, unless some very advanced implementation details are encountered.

It a nice programming exercise of implementing something from a spec but we also
want to make FileCheck.py to conform to the same contract this is why
FileCheck.py is tested using LIT and the LLVM's FileCheck:

First, the LLVM FileCheck is run against a LIT/FileCheck test suite, then
FileCheck.py is run on the same tests to make sure that it has the same behavior
as the LLVM FileCheck.
