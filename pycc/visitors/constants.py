"""AST visitors related to constant values."""

import ast

from . import base


class AssignmentCounter(ast.NodeVisitor):
    """Visitor which returns the number of assignments for a given variable."""

    def __init__(self, name):

        self._name = name
        self._count = 0

    def visit(self, node):

        super(AssignmentCounter, self).visit(node)
        return self._count

    def increment(self):
        """Add one to the counter."""

        self._count += 1

    def visit_Assign(self, node):

        for target in node.targets:

            if (isinstance(target, ast.Name) and
                    target.id == self._name and
                    isinstance(target.ctx, ast.Store)):

                self.increment()


class ConstantFinder(base.NodeFinder):
    """Return a list of constant values which may be inlined."""

    def visit_Assign(self, node):

        for target in node.targets:

            if (isinstance(target, ast.Name) and
                    isinstance(target.ctx, ast.Store) and
                    AssignmentCounter(target.id).visit(self.root) < 2):

                self.add(node)


class ConstantInliner(ast.NodeTransformer):
    """Inline the value of constants."""

    def __init__(self, constants):

        self._constants = constants

    def _get_constant_by_name(self, name):
        """Get a constant assignment by variable name."""

        return reduce(
            lambda current, next: (
                next if name in (t.id for t in next.targets) else current
            ),
            self._constants,
            None,
        )

    def visit_Name(self, node):

        constant = self._get_constant_by_name(node.id)
        if isinstance(node.ctx, ast.Load) and constant is not None:

            return ast.copy_location(constant.value, constant)

        return self.generic_visit(node)


