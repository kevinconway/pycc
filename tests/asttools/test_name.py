"""Test suite for asttools.name."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pycc.asttools import parse
from pycc.asttools import name
from pycc.asttools import visitor


source = """
test_var = True


def some_closure():
    return test_var


class ClosureClass(object):

    def __init__(self):

        self.test_var = test_var


def looks_like_closure():
    test_var = False
    return test_var


import xyz


def uses_import():

    return xyz


def has_arguments(xyz=None):

    return xyz


fn_ref = some_closure
cls_ref = ClosureClass

built_in = repr
"""


@pytest.fixture
def node():
    """Get as AST node from the source."""
    return parse.parse(source)


@pytest.fixture
def decl_node(node):
    """Get the declaration for test_var."""
    return node.body[0]


@pytest.fixture
def return_node(node):
    """Get the name used by the closure return statement."""
    return node.body[1].body[0].value


@pytest.fixture
def assign_node(node):
    """Get the name used by an assignment in the class method."""
    return node.body[2].body[0].body[0].value


@pytest.fixture
def reassign_decl(node):
    """Get the declaration for a re-assignment of the test_var."""
    return node.body[3].body[0]


@pytest.fixture
def reassign_use(node):
    """Get the usage of the re-assigned test_var."""
    return node.body[3].body[1].value


@pytest.fixture
def import_decl(node):
    """Get the declaration of the imported name."""
    return node.body[4]


@pytest.fixture
def import_use(node):
    """Get the usage of an imported name."""
    return node.body[5].body[0].value


@pytest.fixture
def args_decl(node):
    """Get the declaration of function arguments."""
    return node.body[6].args


@pytest.fixture
def args_use(node):
    """Get the usage of function arguments."""
    return node.body[6].body[0].value


@pytest.fixture
def fn_decl(node):
    """Get the declaration of a function."""
    return node.body[1]


@pytest.fixture
def cls_decl(node):
    """Get the declaration of a class."""
    return node.body[2]


@pytest.fixture
def fn_use(node):
    """Get the usage of a function."""
    return node.body[7].value


@pytest.fixture
def cls_use(node):
    """Get the usage of a class."""
    return node.body[8].value


@pytest.fixture
def builtin_use(node):
    """Get the usage of a built-in name."""
    return node.body[9].value


@pytest.fixture
def name_iter(node):
    """Get iterable of all names in the source."""
    class TestVisitor(visitor.NodeVisitorIter, name.NameVisitorMixin):
        pass

    return TestVisitor(node).visit()


def test_declaration(decl_node, return_node, assign_node):
    """Test that the declaration of a name can be found."""
    assert name.declaration(return_node) is decl_node
    assert name.declaration(assign_node) is decl_node


def test_declaration_reassign(decl_node, reassign_decl, reassign_use):
    """Test that reassignments don't throw off declarations."""
    assert name.declaration(reassign_use) is not decl_node
    assert name.declaration(reassign_use) is reassign_decl


def test_declaration_import(import_decl, import_use):
    """Test that import are also declarations."""
    assert name.declaration(import_use) is import_decl


def test_declaration_args(args_decl, args_use):
    """Test that arguments are also declarations."""
    assert name.declaration(args_use) is args_decl


def test_declaration_fn(fn_decl, fn_use):
    """Test that function definitions are also declarations."""
    assert name.declaration(fn_use) is fn_decl


def test_declaration_cls(cls_decl, cls_use):
    """Test that class definitions are also declarations."""
    assert name.declaration(cls_use) is cls_decl


def test_name_source_adopted(return_node, assign_node):
    """Test that adopted names can be identified."""
    assert name.name_source(return_node) is name.NAME_SOURCE.ADOPTED
    assert name.name_source(assign_node) is name.NAME_SOURCE.ADOPTED


def test_name_source_defined(reassign_use):
    """Test that defined names can be identified."""
    assert name.name_source(reassign_use) is name.NAME_SOURCE.DEFINED


def test_name_source_imported(import_use):
    """Test that import names can be identified."""
    assert name.name_source(import_use) is name.NAME_SOURCE.IMPORTED


def test_name_source_builtin(builtin_use):
    """Test that undefined names are identified."""
    assert name.name_source(builtin_use) is name.NAME_SOURCE.BUILTIN


def test_name_visitor(name_iter):
    """Test that all names appear using the name visitor."""
    tokens = set(n.id for n in name_iter)
    names_to_check = set((
        "test_var",
        "True",
        "some_closure",
        "ClosureClass",
        "__init__",
        "looks_like_closure",
        "xyz",
        "uses_import",
        "has_arguments",
        "fn_ref",
        "cls_ref",
        "built_in",
        "repr",
        "False",
        "None",
        "object",
        "self",
    ))
    assert len(tokens.difference(names_to_check)) == 0
