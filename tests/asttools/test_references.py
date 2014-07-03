import ast

import pytest

from pycc.asttools import references


@pytest.fixture
def node():

    return ast.Assign(
        targets=[ast.Name(id='x', ctx=ast.Store())],
        value=ast.Num(n=1)
    )


def test_parent_references(node):

    references.add_parent_references(node)

    assert node.targets[0].parent is node
    assert node.value.parent is node
    assert node.parent is None


def test_sibling_references(node):

    references.add_sibling_references(node)

    assert node.targets[0].previous is None
    assert node.targets[0].next is node.value
    assert node.value.previous is node.targets[0]
