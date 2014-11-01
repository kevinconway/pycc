============================
PyCC Developer Documentation
============================

Contributing To The Project
===========================

Adding a new optimizer to the core project is (hopefully) a straightforward
process. You are, of course, welcome to use any kind of workflow you like. For
this walkthrough I will be using my own as an example.

Step 1: Create An Extension Object
----------------------------------

The first step is getting your extension bootstrapped into the CLI right away.
This will allow you to use the `pycc-transform` command as soon as your code
is written. Seeing the transformed output early makes it a little easier to
debug and iterate.

Start by creating a new module in the `pycc.cli.extensions` package. Normal
Python naming rules apply. Try to keep it short and descriptive. Inside the
module start with some light scaffolding like:

.. code-block:: python

    """Core extension for some new optimizer."""

    from __future__ import division
    from __future__ import absolute_import
    from __future__ import print_function
    from __future__ import unicode_literals

    from . import interfaces
    from ...optimizers import <my_optimizer_module>


    class MyOptimizerExtension(interfaces.CliExtension):

        """A CLI extension which enables my optimization."""

        name = 'makeitfast'
        description = 'Makes code go fast.'
        arguments = ()

        @staticmethod
        def optimize(node):
            """Make all the code better and faster."""
            <my_optimizer_module>.optimize(node)

This class will act as the entry point for your optimizer and will be used by
the CLI tools.

Step 2: Adding Arguments
------------------------

If you know you want to have CLI arguments to customize the behaviour of your
optimizer then you need to modify the `arguments` property of your extension
class. All arguments you add to the tuple should be instances of the
`interfaces.Arg` class which takes in a `name`, `type`, and `description` at
initialization. For example, if you wanted to add an integer argument:

.. code-block:: python

    arguments = (interfaces.Arg('num-times', int, 'Go x times faster!'),)

This will add a CLI argument called 'makeitfast-num-times'. Each argument will
be prepended by the extension name when it appears on the command line.
However, when you accept this argument in your `optimize` method you should
simply use the argument name with underscores instead of dashes:

.. code-block:: python

    def optimize(node, num_times=1):

        for x in range(num_times):

            <my_optimizer_module>.optimize(node)

All arguments will be passed in as keyword arguments.

Step 3: Adding An Empty Optimizer
---------------------------------

Now create a module with a similar name to your extension module in the
`pycc.optmizers` package. In this module define and empty function called
`optimize`:

.. code-block:: python

    def optimize(node):

        pass

This is where you will implement the actual optimization logic. Leave it blank
just for a moment.

Step 4: Add An Entry Point
--------------------------

In the setup.py file you will find a list of setuptools entry points which link
to other extensions. Add one under `pycc.optimizers` that points back to the
extension class you created in step 1.

.. code-block:: python

    entry_points={
        'console_scripts': [
            'pycc-transform = pycc.cli.transform:main',
            'pycc-compile = pycc.cli.compile:main',
        ],
        'pycc.optimizers': [
            'pycc_constant_inliner = pycc.cli.extensions.constants:ConstantInlineExtension',
            'pycc_makeitfaster = pycc.cli.extensions.makeitfast:MyOptimizerExtension',
        ],
    },

This will register your new extension with the CLI. Now if you do a
`pycc-transform --help` you will see a flag, or flags, added to the CLI that
represent your new addition.

Step 5: Optimize
----------------

All the rest is on you. Implement the body of the `optimize` function in your
`optimizers` module and see the results. All optimization and modifications of
the AST should be done in-place.

How you go about implementing the optimizer is up to you. There are, however,
some tools in PyCC which may prove useful. A full listing of those tools can be
found in the `asttools <api/pycc.asttools.html>`_ and
`astwrapper <api/pycc.astwrappers.html>`_ modules.

Step 6: Test And Lint
---------------------

Before you submit your pull request, make sure it passes all the automated
tests. TravisCI will run them for you, but you can also use the tox setup
packaged with this project. Make sure your code passes PEP8, pyflakes, and
tests in all Python environments (2.6 - 3.4).

You should also add to the tests as you develop your optimizer. Use the
existing tests as a guide if you are unsure where to start. Just make sure
you've given a best effort to make sure the optimizer works correctly. If you
spend a significant amount of time trying to overcome and edge case or bug you
should most certainly make a test that replicates the issue so another
developer doesn't change your code and cause a regression.

AST Tools
=========

Developing Third Party Extensions
=================================

PyCC is designed to treat all optimizers, even the core ones, as extensions.
This makes all the above information applicable to writing your own third
part extension.

The major differences are the, obviously, you will be working in your own code
base rather than this project directly. Since that is the case, the
organization, style, testing framework, and etc. are all up to you. This
project places no constriction on how you develop your own, independent code.

The only exception to this is the extension interface. While you do not have to
use the base classes or tools from PyCC, the extension you expose _must_ match
the standard interface.

The basic requirements for the interface are:

    -   Must have a 'name' property with a short, unique name for the extension.

    -   Must have a 'description' property with a short description of the
        extension.

    -   Must have an 'arguments' property which is an iterable.

    -   Each item present in 'arguments' must expose the following properties:

        -   'name'

            Name of the argument as it appears on the command line.

        -   'description'

            Help message that describes what the flag does.

        -   'type'

            Type object (int, str, etc.) that will be used to type cast the
            value of the flag.

    -   Must expose a function called 'optimize'. This method must:

        -   Accept an `ast.AST` node as the first parameter.

        -   Accept keyword arguments that match the items given in 'arguments'
            above. Note: dashes are replaced with underscores.

Beyond this, the only thing your project must do is provide an entry point
under the `pycc.optimizer` group which points to your extension interface.
