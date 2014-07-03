============================
PyCC Optimizer Documentation
============================

Each PyCC optimizer applies some transformation to your source code. All
optimizers are disabled by default in both the `pycc-transform` and
`pycc-compile` scripts. Below is a list of of optimizations that can be
enabled, a description of what transformation it applies, and the command line
flag needed to enable it.

Constant Inlining
=================

`Flag: --constants`

As demonstrated on the main page, this option replaces the use of read-only,
constant values with their literal values. This affects variables that are
assigned only once within the given scope and are assigned to a number, string,
or name value. Name values are any other symbols including True, False, and
None.

This transformation does not apply to constants that are assigned to complex
types such as lists, tuples, function calls, or generators.
