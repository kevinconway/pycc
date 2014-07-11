"""Finder/Optimizer for inlining constant values."""

import ast

from . import base
from ..asttools import references
from ..asttools import scope


class MultipleAssignmentCheck(base.Check, ast.NodeVisitor):
    """True if given ast.Name is assigned more than once in a scope."""

    def __init__(self, *args, **kwargs):

        super(MultipleAssignmentCheck, self).__init__(*args, **kwargs)
        self._node = None
        self._name = None
        self._count = 0

    def __call__(self, node):

        self._node = node
        self._name = scope.Name(node)
        self._count = 0
        self.visit(self.module.node)

        # Builtins could have 0 assignments. Using != for this reason.
        return self._count != 1

    def visit_Assign(self, node):

        target = node.targets[0] if hasattr(node, 'targets') else node.target

        # Simple "x = y" assignment type.
        if (
            isinstance(target, ast.Name) and
            self._name == scope.Name(target)
        ):

                self._count += 1

        # Complex "x, y = a, b" assignment type.
        if isinstance(target, ast.Tuple):

            for elt in target.elts:

                if (
                    isinstance(elt, ast.Name) and
                    self._name == scope.Name(elt)
                ):

                    self._count += 1
                    break

    visit_AugAssign = visit_Assign

    def visit_Global(self, node):

        for name in node.names:

            global_name = scope.Name(
                references.copy_location(
                    ast.Name(
                        id=name,
                        ctx=ast.Store(),
                    ),
                    node,
                )
            )

            if self._name == global_name:

                # The global keyword is only used in order to modify a name
                # available through a closure. Assume the worst and discount
                # the node.
                self._count += 2


class ComplexTypeCheck(base.Check):
    """True if the first assignment is to a complex type.

    Complex types include anything other than number, string, and names.

    Inlining lists, generator expressions, etc., is usually harmful. Take the
    example of:

        x = [1,2,3]
        for y in len(x):
            print x[y]

    This would be inlined as:

        x = [1,2,3]
        for y in len([1,2,3]):
            print [1,2,3][y]

    While this is technically correct and valid code, it would not produce the
    expected "optimized" code for large length arrays.
    """

    def __call__(self, node):

        declaration = scope.Name(node).declaration

        # Builtins have no declaration
        if declaration is None:

            return False

        if isinstance(declaration, ast.Assign):

            target = declaration.targets[0]
            value = declaration.value

            if isinstance(target, ast.Tuple) and isinstance(value, ast.Tuple):

                for idx, elt in enumerate(target.elts):

                    if isinstance(elt, ast.Name) and elt.id == node.id:

                        value = value.elts[idx]
                        break

            return (
                value is not None and
                not (
                    isinstance(value, ast.Num) or
                    isinstance(value, ast.Str) or
                    isinstance(value, ast.Name)
                )
            )

        return False


class ConstantCheck(base.Check):
    """Check whether or not the value is a constant."""

    def __call__(self, name):

        return (
            not ComplexTypeCheck(self.module)(name) and
            not MultipleAssignmentCheck(self.module)(name)
        )


class ConstantFinder(base.Finder, ast.NodeVisitor):
    """Find where constants are first assigned."""

    def __init__(self, module):

        super(ConstantFinder, self).__init__(module)

        self._found = []

    def __call__(self):

        self._found = []
        self.visit(self.module.node)
        return self._found[:]

    # TODO(kevinconway): Add visit_Import(From).
    def visit_Assign(self, node):

        # Assignments always have one target. Either Name or Tuple type.
        target = node.targets[0]
        value = node.value

        # Simple "x = y" statement
        if isinstance(target, ast.Name):

            if ConstantCheck(self.module)(target):

                self._found.append(
                    base.FinderResult(
                        node=node,
                        module=self.module,
                    )
                )

        # Complex "a, b = x, y" statement
        if isinstance(target, ast.Tuple):

            for idx, elt in enumerate(target.elts):

                if isinstance(elt, ast.Name):

                    if ConstantCheck(self.module)(elt):

                        dupe = references.copy_location(
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
                            )
                        )


class ConstantInliner(base.Transformer, ast.NodeTransformer):
    """Inline the value of constants."""

    def __call__(self, found):

        self._constant = found.node
        self._value = self._resolve_constant_value(found.node, found.module)
        self.visit(found.module.node)

    # TODO(kevinconway): Traverse import paths for values.
    def _resolve_constant_value(self, node, module):

        return node.value

    def visit_Name(self, node):

        if (
            isinstance(node.ctx, ast.Load) and
            node.id in (t.id for t in self._constant.targets)
        ):

            return references.copy_location(
                self._value,
                self._constant,
            )

        return self.generic_visit(node)


def optimize(module):
    """Run the optimization chain for constant value inlining."""

    found = ConstantFinder(module)()

    for item in found:

        ConstantInliner(module)(item)
