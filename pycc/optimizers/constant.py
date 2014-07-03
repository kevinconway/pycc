"""Finder/Optimizer for inlining constant values."""

import ast

from . import base


class ConstantCheck(base.Check, ast.NodeVisitor):
    """Check whether or not the value is a constant."""

    def __init__(self, module, package=None):

        super(ConstantCheck, self).__init__(module, package)
        self._count = 0
        self._complex = False
        self._name = None

    def __call__(self, name):

        self._count = 0
        self._complex = False
        self._name = name
        self.visit(self.module.node)
        return self._count == 1 and not self._complex

    def visit_Assign(self, node):

        value = None
        target = node.targets[0] if hasattr(node, 'targets') else node.target

        # Simple "x = y" assignment type.
        if (isinstance(target, ast.Name) and
                target.id == self._name and
                isinstance(target.ctx, ast.Store)):

                self._count += 1
                value = node.value

        # Complex "x, y = a, b" assignment type.
        if (isinstance(target, ast.Tuple) and
                isinstance(node.value, ast.Tuple)):

            idx = 0
            for elt in target.elts:

                if (isinstance(elt, ast.Name) and
                        elt.id == self._name and
                        isinstance(elt.ctx, ast.Store)):

                    self._count += 1
                    value = node.value.elts[idx]
                    break

                idx += 1

        # Inlining lists, generator expressions, etc., is usually harmful. Take
        # the example of:
        #
        #       x = [1,2,3]
        #       for y in len(x):
        #           print x[y]
        #
        # This would be inlined as:
        #
        #       x = [1,2,3]
        #       for y in len([1,2,3]):
        #           print [1,2,3][y]
        #
        # While this is technically correct and valid code, it would not
        # produce the expected "optimized" code for large length arrays.
        if (value is not None and
            not (isinstance(value, ast.Num) or
                 isinstance(value, ast.Str) or
                 isinstance(value, ast.Name))):

            self._complex = True

    visit_AugAssign = visit_Assign


class ConstantFinder(base.Finder, ast.NodeVisitor):
    """Find where constants are first assigned."""

    def __init__(self, module, package=None):

        super(ConstantFinder, self).__init__(module, package)

        self._found = []

    def __call__(self):

        self._found = []
        self.visit(self.module.node)
        return self._found[:]

    def visit_Assign(self, node):

        # Assignments always have one target. Either Name or Tuple type.
        target = node.targets[0]
        value = node.value

        # Sanity check to ensure this is a STORE call.
        if isinstance(target.ctx, ast.Store):

            # Simple "x = y" statement
            if isinstance(target, ast.Name):

                if ConstantCheck(self.module, self.package)(target.id):

                    self._found.append(
                        base.FinderResult(
                            node=node,
                            module=self.module,
                            package=self.package,
                        )
                    )

            # Complex "a, b = x, y" statement
            if isinstance(target, ast.Tuple):

                for idx, elt in enumerate(target.elts):

                    if isinstance(elt, ast.Name):

                        if ConstantCheck(self.module, self.package)(elt.id):

                            dupe = ast.copy_location(
                                ast.Assign(
                                    targets=[target.elts[idx]],
                                    value=value.elts[idx],
                                ),
                                node,
                            )

                            self._found.append(
                                base.FinderResult(
                                    node=dupe,
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
