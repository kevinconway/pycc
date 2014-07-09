import ast
import os

import pytest

from pycc import module
from pycc.asttools import imports


@pytest.fixture
def mod():

    return module.Module(
        path='/one/two/three/four/five',
        location=None,
        node=None,
        package=None,
    )


def test_normalized_import_simple(mod):

    assert imports.normalized_import(
        node=ast.Import(
            names=[ast.alias(name="a.b.c.d", asname=None)],
        ),
        module=mod,
    )[0] == os.path.join('/', 'a','b','c','d')


def test_normalized_import_relative_in_bounds(mod):

    assert imports.normalized_import(
        node=ast.ImportFrom(
            module='four',
            names=[ast.alias(name='cool_feature', asname='cool')],
            level=2,
        ),
        module=mod,
    )[0] == os.path.join('/', 'one', 'two', 'three', 'four', 'cool_feature')


def test_normalized_import_relative_out_bounds(mod):

    assert imports.normalized_import(
        node=ast.ImportFrom(
            module='four',
            names=[ast.alias(name='cool_feature', asname='cool')],
            level=8,
        ),
        module=mod,
    )[0] == os.path.join('/', 'four', 'cool_feature')
