"""AST visitors for reverse looping based on index."""

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
        self.itervar = node.iter.args[0].left.args[0].id

        self.generic_visit(node)

        return self.found_subscript

    def visit_Subscript(self, node):

        if (isinstance(node.value, ast.Name) and
                node.value.id == self.itervar and
                isinstance(node.slice, ast.Index) and
                isinstance(node.slice.value, ast.Name) and
                node.slice.value.id == self.loopvar):

            self.found_subscript = True


class ReversedRangeFinder(base.NodeFinder):
    """Return a list of for loops that."""

    def visit_For(self, node):

        if (isinstance(node.iter, ast.Call) and
                node.iter.func.id.endswith('range') and
                isinstance(node.iter.func.ctx, ast.Load) and
                isinstance(node.iter.args[0], ast.BinOp) and
                isinstance(node.iter.args[1], ast.Num) and
                isinstance(node.iter.args[2], ast.Num) and
                isinstance(node.iter.args[0].left, ast.Call) and
                len(node.iter.args) == 3 and
                node.iter.args[0].left.func.id == 'len' and
                # Cannot replace when arg of len is not a name. Ex: inline list
                isinstance(node.iter.args[0].left.args[0], ast.Name) and
                isinstance(node.iter.args[0].op, ast.Sub) and
                isinstance(node.iter.args[0].right, ast.Num) and
                node.iter.args[0].right.n == 1 and
                node.iter.args[1].n == -1 and
                node.iter.args[2].n == -1 and
                IndexAccessDetector().visit(node)):

            self.add(node)


class ReversedIterReplacer(ast.NodeTransformer):
    """Replace reversed index based loops with reversed iter loops."""

    def __init__(self, *args, **kwargs):

        self.loopvar = None
        self.itervar = None

    def visit(self, node):

        return super(ReversedIterReplacer, self).visit(node)

    def visit_For(self, node):

        self.loopvar = node.target
        self.itervar = node.iter.args[0].left.args[0]

        node.iter = ast.copy_location(
            ast.Call(
                func=ast.Name(
                    id='reversed',
                    ctx=ast.Load()
                ),
                args=[self.itervar],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
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
