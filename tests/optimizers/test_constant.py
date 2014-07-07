import ast

import pytest

from pycc import module
from pycc.asttools import parse
from pycc.optimizers import constant


@pytest.fixture
def node():

    return parse.parse(
        """ONE = 1
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
print EIGHT, NINE"""
    )


@pytest.fixture
def mod(node):

    return module.Module(location='/', path=None, node=node)


def test_constant_check_identifies_constants(mod):

    assert constant.ConstantCheck(mod)('ONE') is True
    assert constant.ConstantCheck(mod)('TWO') is True
    assert constant.ConstantCheck(mod)('THREE') is True
    assert constant.ConstantCheck(mod)('SEVEN') is True
    assert constant.ConstantCheck(mod)('EIGHT') is True
    assert constant.ConstantCheck(mod)('NINE') is True


def test_constant_check_discards_multiple_assignements(mod):

    assert constant.ConstantCheck(mod)('FIVE') is False


def test_constant_check_discards_complex_types(mod):

    assert constant.ConstantCheck(mod)('FOUR') is False
    assert constant.ConstantCheck(mod)('SIX') is False


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
