"""Utilities for adding node references to AST nodes."""

import ast


def add_parent_references(node):
    """Add a parent backref to all child nodes."""

    nodes = [node]
    node.parent = None

    while len(nodes) > 0:

        current_node = nodes.pop()
        for child in ast.iter_child_nodes(current_node):

            nodes.append(child)
            child.parent = current_node


def add_sibling_references(node):
    """Add sibling references to all child nodes."""

    nodes = [node]

    while len(nodes) > 0:

        current_node = nodes.pop()
        children = list(ast.iter_child_nodes(current_node))

        nodes += children

        if len(children) < 1:
            continue

        children[0].previous = None
        children[-1].next = None

        if len(children) == 2:
            children[0].next = children[1]
            children[1].previous = children[0]

        if len(children) > 2:
            children[0].next = children[1]
            children[-1].previous = children[-2]

            for index, child in enumerate(children[1:-1]):

                # Offset to match original iterable
                index += 1
                child.previous = children[index - 1]
                child.next = children[index + 1]


def copy_location(new_node, old_node):
    """ast.copy_location wrapper that also copies node references."""

    new_node = ast.copy_location(new_node, old_node)
    new_node.parent = old_node.parent
    new_node.previous, new_node.next = old_node.previous, old_node.next

    return new_node
