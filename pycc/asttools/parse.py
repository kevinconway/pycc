import ast

from . import references


def parse(source, filename='<unknown>', mode='exec'):
    """ast.parse wrapper that adds special node attributes."""

    node = ast.parse(source, filename, mode)
    references.add_parent_references(node)
    references.add_sibling_references(node)

    return node
