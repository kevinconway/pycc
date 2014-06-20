====
PyCC
====

**Python code optimizer.**

Running The Samples
===================

.. code-block::

    pycc-transform samples/constants.py --constants

    pycc-compile samples/reversed_range.py --reversedrange

Usage
=====

-   pycc-transform

    Print a modified source code to the terminal.

-   pycc-compile

    Create a compiled binary instead of printing.

Options
-------

-   --constants

    Render all constants as inline values.

-   --forlist

    Replace inline, sequential lists with xrange where possible.

-   --rangelen

    Convert `range(len())` loops into loops using `__iter__`.

-   --reversedrange

    Convert `range(len()-1, -1 ,-1)` into loops using `reversed()`.

License
=======

::

    Copyright 2014 Kevin Conway

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


Contributing
============

All contributions to this project are protected under the agreement found in
the `CONTRIBUTING` file. All contributors should read the agreement but, as
a summary::

    You give us the rights to maintain and distribute your code and we promise
    to maintain an open source distribution of anything you contribute.
