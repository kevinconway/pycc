"""Test suite for asttools.name."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools

import pytest

from pycc.asttools import parse
from pycc.astwrappers import name


source = """
assign_once = True
assign_multi = False
assign_multi = None

reference_somewhere = 123

def use_reference():
    print(assign_once)
    return reference_somewhere

read_with_global = 321

def read_global():
    global read_with_global
    return read_with_global

write_with_global = 98

def write_global():
    global write_with_global
    write_with_global = 89

from fake_module import imported_name

def function_name():
    pass

class ClassName(object):
    pass
"""


@pytest.fixture
def node():
    """Get as AST node from the source."""
    return parse.parse(source)


def test_name_generator(node):
    """Test that name wrappers can be produced from an AST."""
    names = name.NameGenerator(node).visit()
    tokens = set(n.token for n in names)
    expected_tokens = set((
        'assign_once',
        'True',
        'assign_multi',
        'False',
        'None',
        'reference_somewhere',
        'use_reference',
        'print',
        'read_with_global',
        'read_global',
        'write_with_global',
        'write_global',
        'global',
        'fake_module',
        'imported_name',
        'function_name',
        'ClassName',
        'object',
    ))
    difference = tokens.difference(expected_tokens)
    assert len(difference) == 0


def test_returns_uses(node):
    """Test that the wrapper can return all uses of a name."""
    name_wrap = functools.reduce(
        lambda p, n: n if n.token == 'reference_somewhere' else p,
        name.NameGenerator(node).visit(),
        None,
    )
    assert len(tuple(name_wrap.uses)) == 2


def test_returns_assignments(node):
    """Test that the wrapper can return all assignments of a name."""
    name_wrap = functools.reduce(
        lambda p, n: n if n.token == 'assign_multi' else p,
        name.NameGenerator(node).visit(),
        None,
    )
    assert len(tuple(name_wrap.assignments)) == 2
    assert name_wrap.constant is False


def test_detects_constants(node):
    """Test that the wrapper can identify constant values."""
    name_wrap = functools.reduce(
        lambda p, n: n if n.token == 'assign_once' else p,
        name.NameGenerator(node).visit(),
        None,
    )
    assert len(tuple(name_wrap.uses)) > 1
    assert len(tuple(name_wrap.assignments)) == 1
    assert name_wrap.constant is True
