"""Test suite for asttools.compiler."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pycc.asttools import parse
from pycc.asttools import compiler

source = """
x = True
for y in range(10):
    pass
"""


@pytest.fixture
def node():
    """Get as AST node from the source."""
    return parse.parse(source)


def test_bytecode_compiler(node):
    """Ensure that bytecode can be generated without errors."""
    compiler.ByteCodeCompiler()(node)


def test_source_code_compilter(node):
    """Ensure that source code can be generated without errors."""
    compiler.SourceCodeCompiler()(node)
