import ast

import pytest

from pycc import module
from pycc.asttools import parse
from pycc.optimizers import constant


@pytest.fixture
def node():

    src = """
ONE = 1
TWO = 2
THREE = 3
FOUR = THREE + ONE

FIVE = THREE
FIVE += TWO

SIX = [1,2,3,]

SEVEN = THREE

EIGHT, NINE = True, False

print ONE
print TWO
print THREE
print FOUR
print FIVE
print SIX
print SEVEN
print EIGHT, NINE
    """

    return parse.parse(src)


@pytest.fixture
def mod(node):

    return module.Package('/').add('/', node)


def test_constant_check_identifies_constants(mod):

    body = mod.node.body
    assert constant.ConstantCheck(mod)(body[0].targets[0]) is True
    assert constant.ConstantCheck(mod)(body[1].targets[0]) is True
    assert constant.ConstantCheck(mod)(body[2].targets[0]) is True
    assert constant.ConstantCheck(mod)(body[7].targets[0]) is True
    assert constant.ConstantCheck(mod)(body[8].targets[0].elts[0]) is True
    assert constant.ConstantCheck(mod)(body[8].targets[0].elts[1]) is True


def test_constant_check_discards_multiple_assignements(mod):

    assert constant.ConstantCheck(mod)(mod.node.body[4].targets[0]) is False


def test_constant_check_discards_complex_types(mod):

    assert constant.ConstantCheck(mod)(mod.node.body[3].targets[0]) is False
    assert constant.ConstantCheck(mod)(mod.node.body[6].targets[0]) is False


def test_constant_finder_matches_check(mod):

    results = constant.ConstantFinder(mod)()

    assert len(results) == 6


def test_contants_are_inlined(mod):

    for result in constant.ConstantFinder(mod)():

        constant.ConstantInliner(mod)(result)

    code = list(ast.iter_child_nodes(mod.node))

    assert isinstance(code[-8].values[0], ast.Num)
    assert code[-8].values[0].n == 1

    assert isinstance(code[-7].values[0], ast.Num)
    assert code[-7].values[0].n == 2

    assert isinstance(code[-6].values[0], ast.Num)
    assert code[-6].values[0].n == 3

    assert isinstance(code[-2].values[0], ast.Num)
    assert code[-2].values[0].n == 3

    assert isinstance(code[-1].values[0], ast.Name)
    assert isinstance(code[-1].values[1], ast.Name)
    assert code[-1].values[0].id == 'True'
    assert code[-1].values[1].id == 'False'
