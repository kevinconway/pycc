import pytest

from pycc.asttools import parse
from pycc.asttools import scope


names_source = """
import z
from y import x
import w as v
a = 1
b = 2
m = True
n = False
o = None

def c(d=None, *args, **kwargs):

    e = d
    m = True
    global n
    n = False
    print o

class F(object):

    g = True

    def h(i=""):

        j = -5

    k = g
"""


@pytest.fixture
def node():

    return parse.parse(names_source)


@pytest.fixture
def func_node(node):

    return node.body[8]


@pytest.fixture
def cls_node(node):

    return node.body[9]


def test_NameNodeGenerator_module(node):

    names = tuple(n.id for n in scope.NameNodeGenerator(node))
    assert 'z' in names
    assert 'x' in names
    assert 'v' in names
    assert 'a' in names
    assert 'b' in names
    assert 'm' in names
    assert 'c' in names
    assert 'F' in names


def test_NameNodeGenerator_func(func_node):

    names = tuple(n.id for n in scope.NameNodeGenerator(func_node))
    assert 'd' in names
    assert 'None' in names
    assert 'args' in names
    assert 'kwargs' in names
    assert 'e' in names
    assert 'm' in names
    assert 'n' in names
    assert 'o' in names


def test_NameNodeGenerator_class(cls_node):

    names = tuple(n.id for n in scope.NameNodeGenerator(cls_node))
    assert 'object' in names
    assert 'g' in names
    assert 'True' in names
    assert 'h' in names
    assert 'k' in names


def test_Name_module(node):

    names = scope.NameNodeGenerator(node)
    names = (scope.Name(n, node) for n in names)
    names = tuple(names)

    assert 'z' in names
    assert 'x' in names
    assert 'v' in names
    assert 'a' in names
    assert 'b' in names
    assert 'm' in names
    assert 'c' in names
    assert 'F' in names

    # Check that the node comparison works as well.
    for n in node.body:

        assert n in names


def test_Name_func(func_node):

    names = scope.NameNodeGenerator(func_node)
    names = (scope.Name(n, func_node) for n in names)
    names = tuple(names)

    assert 'd' in names
    assert 'None' in names
    assert 'args' in names
    assert 'kwargs' in names
    assert 'e' in names
    assert 'm' in names
    assert 'n' in names
    assert 'o'

    # Check sourcing rules
    name = reduce(lambda c, n: n if n == 'd' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'None' else c, names)
    assert name.source is scope.NameSource.Builtin

    name = reduce(lambda c, n: n if n == 'args' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'kwargs' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'e' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'm' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'n' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'o' else c, names)
    assert name.source is scope.NameSource.Adopted


def test_Name_class(cls_node):

    names = scope.NameNodeGenerator(cls_node)
    names = (scope.Name(n, cls_node) for n in names)
    names = set(names)

    assert 'object' in names
    assert 'g' in names
    assert 'True' in names
    assert 'h' in names
    assert 'k' in names

    # Check sourcing rules
    name = reduce(lambda c, n: n if n == 'object' else c, names)
    assert name.source is scope.NameSource.Builtin

    name = reduce(lambda c, n: n if n == 'g' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'True' else c, names)
    assert name.source is scope.NameSource.Builtin

    name = reduce(lambda c, n: n if n == 'h' else c, names)
    assert name.source is scope.NameSource.Defined

    name = reduce(lambda c, n: n if n == 'k' else c, names)
    assert name.source is scope.NameSource.Defined


def test_Name_respects_scope_in_comparison(node, func_node):

    mod_names = scope.NameNodeGenerator(node)
    mod_names = (scope.Name(n, node) for n in mod_names)
    mod_names = tuple(mod_names)
    mod_name = reduce(lambda c, n: n if n == 'm' else c, mod_names)

    func_names = scope.NameNodeGenerator(func_node)
    func_names = (scope.Name(n, func_node) for n in func_names)
    func_names = tuple(func_names)
    func_name = reduce(lambda c, n: n if n == 'm' else c, func_names)

    assert mod_name != func_name


def test_Scope_module(node):

    scp = scope.Scope(node)

    assert scp.type is scope.ScopeType.Module

    assert 'z' in scp
    assert 'x' in scp
    assert 'v' in scp
    assert 'a' in scp
    assert 'b' in scp
    assert 'c' in scp
    assert 'F' in scp


def test_Scope_func(func_node):

    scp = scope.Scope(func_node)

    assert scp.type is scope.ScopeType.Function

    assert 'd' in scp
    assert 'None' in scp
    assert 'args' in scp
    assert 'kwargs' in scp
    assert 'e' in scp


def test_Scope_class(cls_node):

    scp = scope.Scope(cls_node)

    assert scp.type is scope.ScopeType.Class

    assert 'object' in scp
    assert 'g' in scp
    assert 'True' in scp
    assert 'h' in scp
    assert 'k' in scp


def test_Scope_upsizes_non_scope_nodes(node):

    scp = scope.Scope(node.body[3])

    assert scp.type is scope.ScopeType.Module
    assert scp.node is node


def test_Name_produces_Scope(func_node):

    scp = scope.Scope(func_node)
    name = scp.__iter__().next()

    assert name.scope == scp
