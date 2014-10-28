"""Test suite for asttools.scope."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pycc.asttools import parse
from pycc.asttools import scope


source = """
def test_func(d=None, *args, **kwargs):

    return d, args, kwargs

class TestClass(object):

    def test_method(self):

        pass
"""


@pytest.fixture
def node():
    """Get as AST node from the source."""
    return parse.parse(source)


@pytest.fixture
def func_node(node):
    """Get the function AST node from the source."""
    return node.body[0]


@pytest.fixture
def cls_node(node):
    """Get the class AST node from the source."""
    return node.body[1]


@pytest.fixture
def method_node(node):
    """Get the function AST of the class method."""
    return node.body[1].body[0]


def test_is_scope(node, func_node, cls_node, method_node):
    """Test that scopes are properly identified."""
    assert scope.is_scope(node) is True
    assert scope.is_scope(func_node) is True
    assert scope.is_scope(cls_node) is True
    assert scope.is_scope(method_node) is True


def test_scope_type(node, func_node, cls_node, method_node):
    """Test that scope types are property identified."""
    assert scope.scope_type(node) is scope.SCOPE_TYPE.MODULE
    assert scope.scope_type(func_node) is scope.SCOPE_TYPE.FUNCTION
    assert scope.scope_type(cls_node) is scope.SCOPE_TYPE.CLASS
    assert scope.scope_type(method_node) is scope.SCOPE_TYPE.FUNCTION


def test_parent_scope(node, func_node, cls_node, method_node):
    """Test that parent scopes can be retrieved from child nodes."""
    assert scope.parent_scope(func_node) is node
    assert scope.parent_scope(cls_node) is node
    assert scope.parent_scope(method_node) is cls_node


def test_child_scopes(node, func_node, cls_node, method_node):
    """Test that child scopes can be iter'ed."""
    assert func_node in scope.child_scopes(node)
    assert cls_node in scope.child_scopes(node)
    assert method_node not in scope.child_scopes(node)
    assert method_node in scope.child_scopes(cls_node)
