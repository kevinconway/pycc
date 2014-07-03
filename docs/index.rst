==================
PyCC Documentation
==================

PyCC is a Python code optimizer. It rewrites your code to make it faster.

.. toctree::
   :maxdepth: 2

   usage
   optimizers
   development

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

Source?
=======

If you want to file a bug, request an optimization, contribute a patch, or just
read through the source then head over to the
`GitHub page <https://github.com/kevinconway/pycc>`_.

License
=======

The project is licensed under the Apache 2 license.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
