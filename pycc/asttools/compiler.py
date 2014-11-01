"""Utilities for compiling AST nodes."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
# Disabling unicode literals to keep py2 text ascii bytes for compiling.

import ast
import io
import time

from astkit.render import SourceCodeRenderer

from .. import pycompat


def _code_to_bytecode_py2(code):
    """Get bytecode for PY2.

    This implementation borrows heavily from the standard lib implementation
    in the py_compile.compile function.
    """
    # Importing in this function because it only contains useful data when
    # loaded in a PY2 environment.
    import py_compile
    import marshal

    bytecode = io.BytesIO('\0\0\0\0')
    py_compile.wr_long(bytecode, time.time())
    marshal.dump(code, bytecode)
    bytecode.seek(0, 0)
    bytecode.write(py_compile.MAGIC)
    return bytecode.getvalue()


def _code_to_bytecode_py3(code):
    """Get bytecode for PY3.

    This implementation leverages the functions used by the new py_compile
    found in the importlib._bootstrap module.
    """
    # Importing in this function because it only exsists in a PY3 environment.
    import importlib._bootstrap
    return importlib._bootstrap._code_to_bytecode(code, time.time())


def _code_to_bytecode(code):
    """Get bytecode from a code object."""
    if pycompat.PY2:

        return _code_to_bytecode_py2(code)

    return _code_to_bytecode_py3(code)


class ByteCodeCompiler(object):

    """Compiler which generates Python bytecode."""

    def __call__(self, node, location='<AST>'):
        """Compile the AST into bytecode."""
        ast.fix_missing_locations(node)
        codeobject = compile(node, location, 'exec')
        return _code_to_bytecode(codeobject)


class SourceCodeCompiler(object):

    """Compiler which generates new Python source code from an AST."""

    def __call__(self, node):
        """Compile the AST into source code."""
        return SourceCodeRenderer.render(node)
