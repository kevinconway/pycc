====
PyCC
====

.. image:: https://travis-ci.org/kevinconway/pycc.svg?branch=master
    :target: https://travis-ci.org/kevinconway/pycc

PyCC is a Python code optimizer. It rewrites your code to make it faster.

`Developer and usage documentation <http://pycc.readthedocs.org/en/latest/>`.


Basic Example
=============

Symbol table (variable) lookups don't seem expensive at first.

.. code-block:: python

    # awesome_module.py

    MAGIC_NUMBER = 7

    for x in xrange(10000000):

        MAGIC_NUMBER * MAGIC_NUMBER

Now let's make a crude benchmark.

.. code-block:: bash

    # Generate bytecode file to skip compilation at runtime.
    python -m compileall awesome_module.py
    # Now get a simple timer.
    time python awesome_module.pyc

    # real    0m0.923s
    # user    0m0.920s
    # sys     0m0.004s

What does PyCC have to say about it?

.. code-block:: bash

    pycc-transform awesome_module.py --constants

.. code-block:: python

    MAGIC_NUMBER = 7
    for x in xrange(10000000):
        (7 * 7)

Neat, but what good does that do?

.. code-block:: bash

    pycc-compile awesome_module.py -- constants
    time python awesome_module.pyc

    # real    0m0.473s
    # user    0m0.469s
    # sys     0m0.004s

How To Get It
=============

.. code-block:: bash

    pip install pycc

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
