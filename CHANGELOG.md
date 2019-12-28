# Changelog

## [Unreleased](https://github.com/stanislaw/FileCheck.py/tree/HEAD)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.11...HEAD)

**Merged pull requests:**

- docs: Roadmap [\#80](https://github.com/stanislaw/FileCheck.py/pull/80) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.10 → 0.0.11 [\#79](https://github.com/stanislaw/FileCheck.py/pull/79) ([stanislaw](https://github.com/stanislaw))

## [v0.0.11](https://github.com/stanislaw/FileCheck.py/tree/v0.0.11) (2019-12-26)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.10...v0.0.11)

**Closed issues:**

- FileCheck.py exits with 141 when run by LIT \(all checks are checked but there is still some input in stdin\) [\#71](https://github.com/stanislaw/FileCheck.py/issues/71)

**Merged pull requests:**

- docs: initial LIT and FileCheck tutorial and updates in other pages  [\#78](https://github.com/stanislaw/FileCheck.py/pull/78) ([stanislaw](https://github.com/stanislaw))
- docs: What is FileCheck [\#77](https://github.com/stanislaw/FileCheck.py/pull/77) ([stanislaw](https://github.com/stanislaw))
- Update FileCheck.pdf: CHECK-NEXT [\#76](https://github.com/stanislaw/FileCheck.py/pull/76) ([stanislaw](https://github.com/stanislaw))
- Switch to reading full input upfront [\#74](https://github.com/stanislaw/FileCheck.py/pull/74) ([stanislaw](https://github.com/stanislaw))

## [v0.0.10](https://github.com/stanislaw/FileCheck.py/tree/v0.0.10) (2019-12-21)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.9...v0.0.10)

## [v0.0.9](https://github.com/stanislaw/FileCheck.py/tree/v0.0.9) (2019-12-21)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.8...v0.0.9)

**Merged pull requests:**

- Workaround to prevent exit 141 \(SIGPIPE\) when exiting while there's still some stdin input [\#73](https://github.com/stanislaw/FileCheck.py/pull/73) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.7 → 0.0.8 [\#70](https://github.com/stanislaw/FileCheck.py/pull/70) ([stanislaw](https://github.com/stanislaw))

## [v0.0.8](https://github.com/stanislaw/FileCheck.py/tree/v0.0.8) (2019-12-20)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.7...v0.0.8)

**Merged pull requests:**

- CHECK-NOT: case when it is the last check but there is still some input [\#69](https://github.com/stanislaw/FileCheck.py/pull/69) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.6 → 0.0.7 [\#68](https://github.com/stanislaw/FileCheck.py/pull/68) ([stanislaw](https://github.com/stanislaw))

## [v0.0.7](https://github.com/stanislaw/FileCheck.py/tree/v0.0.7) (2019-12-19)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.6...v0.0.7)

**Merged pull requests:**

- CHECK: fixing "possible intended match" code by adding another edge case [\#67](https://github.com/stanislaw/FileCheck.py/pull/67) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.5 → 0.0.6 [\#65](https://github.com/stanislaw/FileCheck.py/pull/65) ([stanislaw](https://github.com/stanislaw))

## [v0.0.6](https://github.com/stanislaw/FileCheck.py/tree/v0.0.6) (2019-12-15)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.5...v0.0.6)

**Closed issues:**

- Implement --version  [\#46](https://github.com/stanislaw/FileCheck.py/issues/46)

**Merged pull requests:**

- CHECK-NOT: edge case: failing CHECK has higher precedence than failing CHECK-NOT [\#64](https://github.com/stanislaw/FileCheck.py/pull/64) ([stanislaw](https://github.com/stanislaw))
- CHECK-EMPTY: edge case when it matches the end of input but there are more checks to fail [\#62](https://github.com/stanislaw/FileCheck.py/pull/62) ([stanislaw](https://github.com/stanislaw))
- --version: add more details about filecheck [\#61](https://github.com/stanislaw/FileCheck.py/pull/61) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.4 → 0.0.5 [\#60](https://github.com/stanislaw/FileCheck.py/pull/60) ([stanislaw](https://github.com/stanislaw))

## [v0.0.5](https://github.com/stanislaw/FileCheck.py/tree/v0.0.5) (2019-12-13)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.4...v0.0.5)

**Implemented enhancements:**

- Implement CHECK-NEXT / Regex match [\#54](https://github.com/stanislaw/FileCheck.py/issues/54)

**Merged pull requests:**

- Fix calculation of the current\_scan\_base [\#59](https://github.com/stanislaw/FileCheck.py/pull/59) ([stanislaw](https://github.com/stanislaw))
- CHECK-EMPTY: consistent behavior when followed by normal CHECKS [\#58](https://github.com/stanislaw/FileCheck.py/pull/58) ([stanislaw](https://github.com/stanislaw))
-  Refactoring: extract checks to a separate function  [\#57](https://github.com/stanislaw/FileCheck.py/pull/57) ([stanislaw](https://github.com/stanislaw))
- CHECK-EMPTY: negative match [\#56](https://github.com/stanislaw/FileCheck.py/pull/56) ([stanislaw](https://github.com/stanislaw))
- CHECK-NEXT: negative regex match [\#55](https://github.com/stanislaw/FileCheck.py/pull/55) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.3 → 0.0.4 [\#53](https://github.com/stanislaw/FileCheck.py/pull/53) ([stanislaw](https://github.com/stanislaw))
- Refactoring: remove obsolete code [\#51](https://github.com/stanislaw/FileCheck.py/pull/51) ([stanislaw](https://github.com/stanislaw))

## [v0.0.4](https://github.com/stanislaw/FileCheck.py/tree/v0.0.4) (2019-12-08)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/v0.0.3...v0.0.4)

**Fixed bugs:**

- Check the behavior when a string is passed [\#15](https://github.com/stanislaw/FileCheck.py/issues/15)

**Merged pull requests:**

- Fix scanning for the best intended match  [\#50](https://github.com/stanislaw/FileCheck.py/pull/50) ([stanislaw](https://github.com/stanislaw))
- Bump version: 0.0.2 → 0.0.3  [\#49](https://github.com/stanislaw/FileCheck.py/pull/49) ([stanislaw](https://github.com/stanislaw))
- --version option  [\#48](https://github.com/stanislaw/FileCheck.py/pull/48) ([stanislaw](https://github.com/stanislaw))

## [v0.0.3](https://github.com/stanislaw/FileCheck.py/tree/v0.0.3) (2019-12-05)

[Full Changelog](https://github.com/stanislaw/FileCheck.py/compare/ce965cb5571be21d0c38f6f64c6a85cc9720b620...v0.0.3)

**Implemented enhancements:**

- Feature: --check-prefix option [\#21](https://github.com/stanislaw/FileCheck.py/issues/21)
- Feature: --strict-whitespace option [\#4](https://github.com/stanislaw/FileCheck.py/issues/4)

**Closed issues:**

- Provide help command [\#41](https://github.com/stanislaw/FileCheck.py/issues/41)
- Feature: "note: possible intended match here". [\#10](https://github.com/stanislaw/FileCheck.py/issues/10)

**Merged pull requests:**

- --help command: remove artifacts introduced by testing [\#47](https://github.com/stanislaw/FileCheck.py/pull/47) ([stanislaw](https://github.com/stanislaw))
- Everything what's needed to publish a pip package [\#45](https://github.com/stanislaw/FileCheck.py/pull/45) ([stanislaw](https://github.com/stanislaw))
- Help command: enough to get going [\#44](https://github.com/stanislaw/FileCheck.py/pull/44) ([stanislaw](https://github.com/stanislaw))
- Fix some typos [\#43](https://github.com/stanislaw/FileCheck.py/pull/43) ([AlexDenisov](https://github.com/AlexDenisov))
- Add Poetry [\#42](https://github.com/stanislaw/FileCheck.py/pull/42) ([stanislaw](https://github.com/stanislaw))
- docs: Hello World: minor fixes [\#40](https://github.com/stanislaw/FileCheck.py/pull/40) ([stanislaw](https://github.com/stanislaw))
- docs: "Hello World" tutorial: first version [\#39](https://github.com/stanislaw/FileCheck.py/pull/39) ([stanislaw](https://github.com/stanislaw))
- Print full path to the FileCheck [\#37](https://github.com/stanislaw/FileCheck.py/pull/37) ([stanislaw](https://github.com/stanislaw))
- docs: Tutorial: Hello World some content [\#36](https://github.com/stanislaw/FileCheck.py/pull/36) ([stanislaw](https://github.com/stanislaw))
- .readthedocs.yaml: boilerplate [\#35](https://github.com/stanislaw/FileCheck.py/pull/35) ([stanislaw](https://github.com/stanislaw))
- docs: initial skeleton [\#33](https://github.com/stanislaw/FileCheck.py/pull/33) ([stanislaw](https://github.com/stanislaw))
- FileCheck.pdf: update coverage [\#30](https://github.com/stanislaw/FileCheck.py/pull/30) ([stanislaw](https://github.com/stanislaw))
- Test: CHECK-NOT/one\_string/02-negative\_match\_whitespaces [\#29](https://github.com/stanislaw/FileCheck.py/pull/29) ([stanislaw](https://github.com/stanislaw))
- Refactoring: canonicalize\_whitespace [\#28](https://github.com/stanislaw/FileCheck.py/pull/28) ([stanislaw](https://github.com/stanislaw))
- Feature: CHECK-NOT command: escaping non-regex parts [\#27](https://github.com/stanislaw/FileCheck.py/pull/27) ([stanislaw](https://github.com/stanislaw))
- Tests: regroup CHECK/one\_string tests [\#26](https://github.com/stanislaw/FileCheck.py/pull/26) ([stanislaw](https://github.com/stanislaw))
- Feature: CHECK command: escaping non-regex parts [\#25](https://github.com/stanislaw/FileCheck.py/pull/25) ([stanislaw](https://github.com/stanislaw))
- Feature: check\_commands/CHECK-NEXT and main tests [\#24](https://github.com/stanislaw/FileCheck.py/pull/24) ([stanislaw](https://github.com/stanislaw))
- Features: Stricter CHECK, CHECK-NOT, initial CHECK-NEXT, --check-prefix, --match-full-lines [\#23](https://github.com/stanislaw/FileCheck.py/pull/23) ([stanislaw](https://github.com/stanislaw))
- README: Switch to task list [\#22](https://github.com/stanislaw/FileCheck.py/pull/22) ([stanislaw](https://github.com/stanislaw))
- Refactoring: strip whitespaces "globally" [\#20](https://github.com/stanislaw/FileCheck.py/pull/20) ([stanislaw](https://github.com/stanislaw))
-  Feature: --strict-whitespace/CHECK\_NOT  [\#19](https://github.com/stanislaw/FileCheck.py/pull/19) ([stanislaw](https://github.com/stanislaw))
- Test: options/--strict-whitespace/02\_check\_has\_mixed\_spaces\_and\_tabs/ [\#17](https://github.com/stanislaw/FileCheck.py/pull/17) ([stanislaw](https://github.com/stanislaw))
- Feature: initial options/--strict-whitespace [\#16](https://github.com/stanislaw/FileCheck.py/pull/16) ([stanislaw](https://github.com/stanislaw))
- Tests: CHECK/three\_strings [\#14](https://github.com/stanislaw/FileCheck.py/pull/14) ([stanislaw](https://github.com/stanislaw))
- Regroup tests in a more meaningful way [\#13](https://github.com/stanislaw/FileCheck.py/pull/13) ([stanislaw](https://github.com/stanislaw))
- Feature: note: possible intended match here [\#12](https://github.com/stanislaw/FileCheck.py/pull/12) ([stanislaw](https://github.com/stanislaw))
- Maintain a scan window to present a "scanning from here" line [\#11](https://github.com/stanislaw/FileCheck.py/pull/11) ([stanislaw](https://github.com/stanislaw))
- CHECK/two\_strings/04-negative\_match\_second\_string/sample.itest: complete most of the checks [\#9](https://github.com/stanislaw/FileCheck.py/pull/9) ([stanislaw](https://github.com/stanislaw))
- two\_strings/03-negative\_match\_first\_string/sample.itest: complete the checks [\#8](https://github.com/stanislaw/FileCheck.py/pull/8) ([stanislaw](https://github.com/stanislaw))
- All tests: switch to --match-full-lines [\#6](https://github.com/stanislaw/FileCheck.py/pull/6) ([stanislaw](https://github.com/stanislaw))
- Update README [\#5](https://github.com/stanislaw/FileCheck.py/pull/5) ([stanislaw](https://github.com/stanislaw))
- CHECK-NOT command: more tests [\#3](https://github.com/stanislaw/FileCheck.py/pull/3) ([stanislaw](https://github.com/stanislaw))
- Fix test: CHECK/one\_string/01-negative\_match [\#2](https://github.com/stanislaw/FileCheck.py/pull/2) ([stanislaw](https://github.com/stanislaw))
- Feature: CHECK-NOT/one\_string/01-negative\_match [\#1](https://github.com/stanislaw/FileCheck.py/pull/1) ([stanislaw](https://github.com/stanislaw))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
