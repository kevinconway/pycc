========================
PyCC Usage Documentation
========================

PyCC offers two command line utilities: pycc-transform and pycc-compile.

Transforming Code
=================

PyCC is quite a young project. As a result, you may be hesitant to simply trust
the output and skip straight to the compile step. Instead, you may want to
see an example of what the optimizer has produced so you can verify that
it is, indeed, both valid Python and acceptable code. This is what the
`pycc-transform` command is for.

Usage for this command is simple:

    pycc-transform --source=<python_file.py> [--optimizer_option]

All optimization is disabled by default. Use the appropriate flags to enable
the optimizations you want to apply. At the time of writing the full options
listing for pycc-transform was:

    usage: pycc-transform [-h] --source SOURCE [--destination DESTINATION]
                      [--constants]

    PyCC Transformer

    optional arguments:
      -h, --help            show this help message and exit
      --source SOURCE       Path to load the Python source from.
      --destination DESTINATION
                            Path to place the optimized result or "stdout".
      --constants           Inline constant values.

Running this command will generate a file called <python_file>_optimized.py
that you can view. To print the results directly to the terminal simply add the
'--destination="stdout"' option.

If you run pycc-transform and it produces invalid Python code or it changes the
code such that it no longer does what it is supposed to do then please post the
original source and optimization options enabled as a bug on the
`project GitHub page <https://github.com/kevinconway/pycc>`_.

Compiling Code
==============

Once you are comfortable with the way PyCC alters your code you can start
running the `pycc-compile` command:

    usage: pycc-compile [-h] --source SOURCE [--destination DESTINATION]
                    [--constants]

    PyCC Compiler

    optional arguments:
      -h, --help            show this help message and exit
      --source SOURCE       Path to load the Python source from.
      --destination DESTINATION
                            Path to place the optimized result or "stdout".
      --constants           Inline constant values.

The compiler can be run on either individual Python modules or it can be
pointed at a Python package. By default the script will drop the '.pyc' files
right next to the source files just like the normal Python compiler.
Alternatively you may use the 'destination' option to direct the '.pyc' files
to another directory.

The Python compiler will overwrite existing '.pyc' files every time a source
file is updated. The 'destination' option is useful if you want to create a
compiled version of a module or package that doesn't get overwritten every time
you make a change to the source.
