============================
PyCC Developer Documentation
============================

Contributing To The Project
===========================

Adding a new optimizer to the core project is (hopefully) a straightforward
process. You are, of course, welcome to use any kind of workflow you like. For
this walkthrough I will be using my own as an example.

Step 1: Light Scaffolding
-------------------------

The first step is getting the CLI utilities bootstrapped for you new optimizer
so you can use the `pycc-transform` command to help iterate and work out bugs.

Start by creating a new module in the `optimizers` subpackage to house your
work, name it something relevant, and put function in it named `optimize` that
has the following signature:

.. code-block:: python

    function optimize(module, *args, **kwargs):

        pass

This function will be run by the CLI tools to execute your optimization chain.
The first argument with always be a `module.Module` object. The rest of the
arguments are determined by the CLI. If your optimizer is configurable then
you may add additional named arguments after 'module'.

Now add a line like `pycc_my_optimizer = pycc.optimizers.my_optimizer:optimize`
to the `pycc.optimizers` section in `setup.py`. The `pycc_` prefix is important
so don't leave it off.

Finally, add a new argument to the parser in the `register` function of the
`cli.args` module. Example:

.. code-block:: python

    parser.add_argument(
        '--my_optimizer',
        help="Makes stuff go faster.",
        action='store_const',
        default=None,
        const="pycc_my_optimizer",
    )

The value of the `const` parameter should match the name you selected in the
`pycc.optimizers` entry points from above.

If you want to make a configuration value for your optimizer accessible as a
CLI flag then you may add additional arguments to the parser. Just be sure to
choose a name that is not so generic as to cause conflicts. All CLI arguments
will be passed to your `optimize` function as keyword arguments. You can
collect the values either through the `**kwargs` interface or by simply
accepting a named parameter in the `optimize` function.

Once you have this basic scaffolding set up you will be able to see your new
optimizer flag in the command line scripts. As you add actual code you will be
able to see immediate results by running the `pycc-transform` command.

Step 2: Write A Finder
----------------------

The next step is implementing the `optimizers.base.Finder` interface. The
interface is simple. Basically it must return an iterable of
`optimizers.base.FinderResult` objects when called. The logic used to find
the AST nodes related to your particular optimization is up to you. I found
it useful to use the
`ast.NodeVisitor <https://docs.python.org/2/library/ast.html#ast.NodeVisitor>`_
class to easily walk the AST.

The basic idea behind the Finder is to group together all the logic needed to
identify the AST node(s) required to perform the transformation. For example,
the `optimizers.constant.ConstantFinder` pushes out `FinderResult` objects
containing the `ast.Assign` node for any constant values it finds.

Step 3: Write A Transformer
---------------------------

A transformer is an implementation of `optimizers.base.Transformer`. It accepts
a `FinderResult` as an argument to the call and modifies the AST in any way
required to apply the optimization. The logic that applies the AST
transformation is up to you. I found it useful to use the
`ast.NodeTransformer <https://docs.python.org/2/library/ast.html#ast.NodeTransformer>`_
class for this purpose.

Easy mistakes to avoid:

Make sure to use the `ast.copy_location` if you are replacing a node. You will
likely experience some errors with generating the transformed code if you
don't.

If you decide to the the `ast.NodeTransformer` make sure return the results
of `self.generic_visit(node)` any time you do *not* alter the node. Forgetting
this step could case a large portion of the code to disappear.

Step 4: Optimize And Iterate
----------------------------

The `optimize` function you created in step one is the primary entry point for
your new optimization. It should run your Finder and pass all the results
through your Transformer. Once you implement this function you will start to
see results through the `pycc-transform` command.

Use the command line client on some sample code and iterate until you feel it's
right.

Step 5: Test And Lint
---------------------

Make sure the code passes PEP8 and PyFlakes. Those are the linters that
Travis will run. Also be sure to add some test coverage for the Finder and
Transformer. We're using `py.test`.

Developing Third Party Extensions
=================================

Writing third party extensions that plug into the PyCC commands requires you
to provide two interfaces on the right entry points.

On the `pycc.optimizers` entry point you must expose a callable which accepts
a `module.Module` object as the first parameter, any number of named parameters
which correspond with relevant CLI args added by your module, `*args`,
and`**kwargs`. The name of this entry point must be prefixed with `pycc_`.

On the `pycc.cli.args` entry point you must expose a callable which accepts
an argument parser from `argparse`. Your function must use this parser to
register an argument as follows:

.. code-block:: python

    parser.add_argument(
        '--my_optimizer',
        help="Makes stuff go faster.",
        action='store_const',
        default=None,
        const="pycc_my_optimizer",
    )

The value of the `const` parameter should match exactly the name give to the
`pycc.optimizers` entry point.

You may also register arguments needed to configure your optimizer. They will
be passed into your `pycc.optimizers` entry point addition as keyword
arguments.
