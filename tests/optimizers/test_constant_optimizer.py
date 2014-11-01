"""Test suite for optimizers.constant."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ast

import pytest

from pycc.asttools import parse
from pycc.optimizers import constant

source = """
ONE = 1
TWO = 2
THREE = ONE + TWO
FOUR = THREE + ONE
FIVE = THREE + TWO

def return_const():
    return FOUR

def return_var():
    return FIVE

FIVE = FIVE + ONE
FIVE -= ONE
"""


@pytest.fixture
def node():
    """Get as AST node from the source."""
    return parse.parse(source)


def test_constant_inliner(node):
    """Test that constant values are inlined."""
    constant.optimize(node)

    # Check assignment values using constants.
    assert node.body[2].value.n == 3
    assert node.body[3].value.n == 4
    assert node.body[4].value.n == 5

    # Check return val of const function.
    assert isinstance(node.body[5].body[0].value, ast.Num)
    assert node.body[5].body[0].value.n == 4

    # Check return val of var function.
    assert isinstance(node.body[6].body[0].value, ast.Name)
    assert node.body[6].body[0].value.id == 'FIVE'
