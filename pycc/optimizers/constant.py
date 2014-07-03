"""Finder/Optimizer for inlining constant values."""

import ast

from . import base


class ConstantCheck(base.Check, ast.NodeVisitor):
    """Check whether or not the value is a constant."""

    def __init__(self, module, package=None):

        super(ConstantCheck, self).__init__(module, package)
        self._count = 0
        self._name = None

    def __call__(self, name):

        self._count = 0
        self._name = name
        self.visit(self.module.node)
        return self._count < 2

    def visit_Assign(self, node):

        for target in node.targets:

            if (isinstance(target, ast.Name) and
                    target.id == self._name and
                    isinstance(target.ctx, ast.Store)):

                self._count += 1


class ConstantFinder(base.Finder, ast.NodeVisitor):

    def __init__(self, module, package=None):

        super(ConstantFinder, self).__init__(module, package)

        self._found = []

    def __call__(self):

        self._found = []
        self.visit(self.module.node)
        return self._found[:]

    def visit_Assign(self, node):

        for target in node.targets:

            check = ConstantCheck(
                self.module,
                self.package,
            )
            if (isinstance(target, ast.Name) and
                    isinstance(target.ctx, ast.Store) and
                    check(target.id) is True):

                self._found.append(
                    base.FinderResult(
                        node=node,
                        module=self.module,
                        package=self.package,
                    )
                )


class ConstantInliner(base.Transformer, ast.NodeTransformer):
    """Inline the value of constants."""

    def __call__(self, found):

        self._constant = found.node
        self.visit(found.module.node)

    def visit_Name(self, node):

        if (isinstance(node.ctx, ast.Load) and
                node.id in (t.id for t in self._constant.targets)):

            return ast.copy_location(self._constant.value, self._constant)

        return self.generic_visit(node)


def optimize(module, package=None):
    """Run the optimization chain for constant value inlining."""

    found = ConstantFinder(module, package=package)()

    for item in found:

        ConstantInliner(module, package=package)(item)
