"""Test suite for asttools.references."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ast

import pytest

from pycc.asttools import references


@pytest.fixture
def node():
    """Get an ast.Assign node of 'x = 1'."""
    return ast.Assign(
        targets=[ast.Name(id='x', ctx=ast.Store())],
        value=ast.Num(n=1)
    )


def test_parent_references(node):
    """Test that parent references are added to child nodes."""
    references.add_parent_references(node)

    assert node.targets[0].parent is node
    assert node.value.parent is node
    assert node.parent is None


def test_sibling_references(node):
    """Test that sibling references are added to child nodes."""
    references.add_sibling_references(node)

    assert node.targets[0].previous is None
    assert node.targets[0].next is node.value
    assert node.value.previous is node.targets[0]


def test_copy_location(node):
    """Test that references are preserved by the custom copy_location."""
    references.add_parent_references(node)
    references.add_sibling_references(node)

    original = node.targets[0]
    dupe = references.copy_location(
        ast.Name(id='y', ctx=ast.Store()),
        original,
    )

    assert dupe.parent is original.parent
    assert dupe.previous is original.previous
    assert dupe.next is original.next


def test_get_top_node(node):
    """Test that the root node can be retrieved from any node."""
    references.add_parent_references(node)
    references.add_sibling_references(node)

    assert references.get_top_node(node) is node
    assert references.get_top_node(node.targets[0]) is node
