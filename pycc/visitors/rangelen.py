"""AST visitors for unnecessary index looping."""

import ast

from . import base


class IndexAccessDetector(ast.NodeVisitor):
    """Determine if index access is used in the loop body."""

    def __init__(self):

        self.loopvar = None
        self.itervar = None
        self.found_subscript = False

    def visit(self, node):

        return super(IndexAccessDetector, self).visit(node)

    def visit_For(self, node):

        # Assuming only one loop var based on Finder that passes values in.
        self.loopvar = node.target.id
        self.itervar = node.iter.args[0].args[0].id

        self.generic_visit(node)

        return self.found_subscript

    def visit_Subscript(self, node):

        if (isinstance(node.value, ast.Name) and
                node.value.id == self.itervar and
                isinstance(node.slice, ast.Index) and
                isinstance(node.slice.value, ast.Name) and
                node.slice.value.id == self.loopvar):

            self.found_subscript = True


class RangeLenFinder(base.NodeFinder):
    """Return a list of for loops that."""

    def visit_For(self, node):

        if (isinstance(node.iter, ast.Call) and
                node.iter.func.id.endswith('range') and
                isinstance(node.iter.func.ctx, ast.Load) and
                isinstance(node.iter.args[0], ast.Call) and
                node.iter.args[0].func.id == 'len' and
                isinstance(node.iter.args[0].args[0], ast.Name) and
                IndexAccessDetector().visit(node)):

            self.add(node)


class IterLoopReplacer(ast.NodeTransformer):
    """Replace index based loops with iter loops."""

    def __init__(self, *args, **kwargs):

        self.loopvar = None
        self.itervar = None

    def visit(self, node):

        return super(IterLoopReplacer, self).visit(node)

    def visit_For(self, node):

        self.loopvar = node.target
        self.itervar = node.iter.args[0].args[0]

        node.iter = ast.copy_location(
            self.itervar,
            node.iter,
        )

        return self.generic_visit(node)

    def visit_Subscript(self, node):

        if (isinstance(node.value, ast.Name) and
                node.value.id == self.itervar.id and
                isinstance(node.slice, ast.Index) and
                isinstance(node.slice.value, ast.Name) and
                node.slice.value.id == self.loopvar.id):

            return self.loopvar

        return self.generic_visit(node)
