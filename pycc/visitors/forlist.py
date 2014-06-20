"""AST visitors related looping over lists of numbers."""

import ast

from . import base


class SequentialListDetector(ast.NodeVisitor):
    """Determines whether or not a list is made of sequential numbers."""

    def visit(self, node):

        return super(SequentialListDetector, self).visit(node)

    def visit_List(self, node):

        if isinstance(node.ctx, ast.Load):

            if node.elts:

                for i, v in enumerate(node.elts):

                    if not isinstance(v, ast.Num) or v.n != i :

                        return False

                return True

        return False

    visit_Tuple = visit_List


class ForListFinder(base.NodeFinder):
    """Return a list of for loops that."""

    def visit_For(self, node):

        if ((isinstance(node.iter, ast.Tuple) or
                isinstance(node.iter, ast.List)) and
                SequentialListDetector().visit(node.iter)):

            self.add(node)


class XRangeReplacer(ast.NodeTransformer):
    """Replace iters over lists with xrange."""

    def __init__(self, loops):

        self._loops = loops

    def visit_For(self, node):

        if node in self._loops:

            node.iter = ast.copy_location(
                ast.Call(
                    func=ast.Name(
                        id='xrange',
                        ctx=ast.Load()
                    ),
                    args=[ast.Num(n=len(node.iter.elts))],
                    keywords=[],
                    starargs=None,
                    kwargs=None
                ),
                node.iter,
            )

        return self.generic_visit(node)


