"""Utilities for iterating over child AST nodes."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ast
import itertools


class NodeVisitorShallow(ast.NodeVisitor):

    """Stand-in for ast.NodeVisitor which is non-recursive.

    This visitor only looks at first generation children and does not descend
    into children of children, etc.
    """

    def visit(self, node):
        """Visit a node.

        This function will look at the instance of NodeVisitorShallow for a
        method which matches visit_<Node> where <Node> matches the name of an
        ast.AST class. This behaviour matches that of the standard
        ast.NodeVisitor.

        This implementation differs from the standard in that it will only
        search the first order children of a given node. The given node is also
        processed. The generic_visit method is also not used in this
        implementation.

        This method does not return a value.
        """
        for child in itertools.chain((node,), ast.iter_child_nodes(node)):

            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, None)
            if visitor is not None:

                visitor(node)


class NodeVisitorDeep(ast.NodeVisitor):

    """Stand-in for ast.NodeVisitor which is non-recursive.

    This visitor looks at all children within the tree represented by the node
    given at initialization.
    """

    def visit(self, node):
        """Visit a node.

        This function will look at the instance of NodeVisitorDeep for a
        method which matches visit_<Node> where <Node> matches the name of an
        ast.AST class. This behaviour matches that of the standard
        ast.NodeVisitor.

        This implementation should be identical to the standard in the way it
        searches and processes AST nodes except that it does not use recursion,
        does not return a value, and does not use the generic_visit method.
        """
        nodes = [node]
        while len(nodes) > 0:

            current = nodes.pop()
            for child in ast.iter_child_nodes(current):

                nodes.append(child)

            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, None)
            if visitor is not None:

                visitor(node)


class NodeIterShallow(ast.NodeVisitor):

    """Stand-in for ast.NodeVisitor which produces an iterable of values.

    This visitor only looks at first generation children and does not descend
    into children of children, etc. The return values of each visitor method
    are returned as an iterable from the visit method.
    """

    def visit(self, node):
        """Visit a node.

        This function will look at the instance of NodeIterShallow for a
        method which matches visit_<Node> where <Node> matches the name of an
        ast.AST class. This behaviour matches that of the standard
        ast.NodeVisitor.

        This implementation differs from the standard in that it will only
        search the first order children of a given node. The given node is also
        processed. The generic_visit method is also not used in this
        implementation.

        This method returns an iterable of values returned by the visit_<Node>
        methods that are executed during the visit.

        If a visitor method returns an iterable then each value will appear
        in the return rather than the iterable itself.
        """
        for child in itertools.chain((node,), ast.iter_child_nodes(node)):

            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, None)
            if visitor is not None:

                visit_value = visitor(node)
                try:

                    for value in visit_value:

                        yield value

                except TypeError:

                    yield visit_value


class NodeIterDeep(ast.NodeVisitor):

    """Stand-in for ast.NodeVisitor which produces an iterable of values.

    This visitor looks at all children within the tree represented by the node
    given at initialization. The return values of each visitor method are
    returned as an iterable from the visit method.
    """

    def visit(self, node):
        """Visit a node.

        This function will look at the instance of NodeVisitorDeep for a
        method which matches visit_<Node> where <Node> matches the name of an
        ast.AST class. This behaviour matches that of the standard
        ast.NodeVisitor.

        This implementation should be identical to the standard in the way it
        searches and processes AST nodes except that it does not use recursion,
        the return value is an iterable of values returned by visit_<Node>
        methods, and it does not use the generic_visit method.

        If a visitor method returns an iterable then each value will appear
        in the return rather than the iterable itself.
        """
        nodes = [node]
        while len(nodes) > 0:

            current = nodes.pop()
            for child in ast.iter_child_nodes(current):

                nodes.append(child)

            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, None)
            if visitor is not None:

                visit_value = visitor(node)
                try:

                    for value in visit_value:

                        yield value

                except TypeError:

                    yield visit_value
