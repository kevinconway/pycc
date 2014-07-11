"""Containers for variable scope rules."""

import ast

from .references import copy_location


class ScopeType(object):
    """Describes the type of scope."""

    # Module/Global scope.
    Module = object()
    # Function scope.
    Function = object()
    # Class scope.
    Class = object()

    @classmethod
    def __iter__(cls):

        return (cls.Module, cls.Function, cls.Class)


class Scope(object):
    """Represents a lexical scope.

    Can be constructed from any AST node. If the node is already the beginning
    of a scope it will be used directly. Otherwise the nearest scope will be
    found.
    """

    __slots__ = ('node', 'type')

    def __init__(self, node):

        self.node = node if Scope.is_scope(node) else Scope.nearest_scope(node)
        self.type = Scope.scope_type(self.node)

    def __iter__(self):
        """Iter over all Names in the scope."""

        for name in NameNodeGenerator(self.node):

            yield Name(name, scope=self.node)

    def __eq__(self, other):
        """Compare Scope objects with other ast nodes or Scope objects.

        If 'other' is Scope => compare that beginning nodes are the same.

        Elif 'other' is ast node => compare identity with beginning node.
        """

        if isinstance(other, Scope):

            return self.node is other.node

        if isinstance(other, ast.AST):

            return self.declaration is other

        raise TypeError("Can only compare Scope with Scope and ast.AST.")

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(self.node)

    def __repr__(self):

        return '{0} - {1}'.format(
            self.node,
            'Module' if self.type is ScopeType.Module else
            'Function' if self.type is ScopeType.Function else
            'Class' if self.type is ScopeType.Class else
            'None',
        )

    @staticmethod
    def is_scope(node):
        """True if the node represents a scope."""

        return (
            isinstance(node, ast.Module) or
            isinstance(node, ast.FunctionDef) or
            isinstance(node, ast.ClassDef)
        )

    @staticmethod
    def nearest_scope(node):
        """Find the AST node that represents the first enclosing scope."""

        node = node.parent if hasattr(node, 'parent') else None

        while node is not None:

            if (
                isinstance(node, ast.Module) or
                isinstance(node, ast.FunctionDef) or
                isinstance(node, ast.ClassDef)
            ):

                return node

            node = node.parent

        raise ValueError("No valid scope found in node path.")

    @staticmethod
    def scope_type(node):
        """Get the ScopeType of a node."""

        if not Scope.is_scope(node):

            raise ValueError("Node must be the beginning of a scope.")

        if isinstance(node, ast.Module):

            return ScopeType.Module

        if isinstance(node, ast.FunctionDef):

            return ScopeType.Function

        if isinstance(node, ast.ClassDef):

            return ScopeType.Class


class NameSource(object):
    """Describes the source of a Name within a given scope."""

    # Defined in the scope.
    Defined = object()
    # Adopted from a higher scope.
    Adopted = object()
    # Adopted from an import statement. Special adoption.
    Imported = object()
    # Part of the Python core.
    Builtin = object()

    @classmethod
    def __iter__(cls):

        return (cls.Defined, cls.Adopted, cls.Imported, cls.Builtin)


class Name(object):
    """Represents a name used within a scope.

    Contains the string token used to represent the name, the ast node where
    the name is first declared, and the NameSource rule that applies.
    """

    __slots__ = ('_name', '_scope', 'token', 'declaration', 'source', 'scope')

    def __init__(self, name, scope=None):

        self._name = name
        self._scope = scope or Scope.nearest_scope(self._name)
        self.declaration = Name.find_declaration(
            self._name,
            start=self._scope,
        )
        self.source = Name.declaration_source(self._name, self.declaration)
        self.token = self._name.id

    @property
    def scope(self):

        return Scope(self._scope)

    def __eq__(self, other):
        """Compare Name objects with other ast nodes or strings.

        If 'other' is ast.Name => create Name and compare.

        Elif 'other' is a Name => compare token and scope.

        Elif 'other' is ast node => compare identity with declaration node.

        Else compare token with other (string comparison assumed).
        """

        if isinstance(other, ast.Name):

            other = Name(other)

        if isinstance(other, Name):

            return self.token == other.token and self.scope == other.scope

        if isinstance(other, ast.AST):

            return self.declaration is other

        return self.token == other

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(self.token)

    def __repr__(self):

        return '<Name {0} - {1}>'.format(
            self.token,
            'Imported' if self.source is NameSource.Imported else
            'Adopted' if self.source is NameSource.Adopted else
            'Defined' if self.source is NameSource.Defined else
            'Builtin' if self.source is NameSource.Builtin else
            'None',
        )

    @staticmethod
    def find_declaration(name, start=None):
        """Find the AST node where a name is first declared.

        The search begins in the same scope as the given ast.Name node. Give
        a Scope object via the 'start' parameter to change the search path.
        """

        scopes = [start or Scope.nearest_scope(name)]

        while len(scopes) > 0:

            scope = scopes.pop()
            for child in ast.iter_child_nodes(scope):

                if (
                    isinstance(child, ast.Import) or
                    isinstance(child, ast.ImportFrom)
                ):

                    for a in child.names:

                        # 'names' always contains ast.alias.
                        if (
                            (a.asname is not None and name.id == a.asname) or
                            (a.asname is None and name.id == a.name)
                        ):

                            return child

                if isinstance(child, ast.Assign):

                    target = child.targets[0]

                    if isinstance(target, ast.Name) and target.id == name.id:

                        return child

                    if isinstance(target, ast.Tuple):

                        for elt in target.elts:

                            if isinstance(elt, ast.Name) and elt.id == name.id:

                                return child

                if (
                    (
                        isinstance(child, ast.FunctionDef) or
                        isinstance(child, ast.ClassDef)
                    ) and child.name == name.id
                ):

                    if child.name == name.id:

                        return child

                if isinstance(child, ast.arguments):

                    if child.vararg == name.id or child.kwarg == name.id:

                        return child

                    for arg in child.args:

                        if arg.id == name.id:

                            return child

            if scope.parent is None:

                return None

            scopes.append(scope.parent)

    @staticmethod
    def declaration_source(name, declaration=None):
        """Get the NameSource for the given name.

        If declaration is not given it will be derived from the given name.
        """

        declaration = declaration or Name.find_declaration(name)

        if declaration is None:

            return NameSource.Builtin

        if (
            isinstance(declaration, ast.Import) or
            isinstance(declaration, ast.ImportFrom)
        ):

            return NameSource.Imported

        if Scope.nearest_scope(name) is Scope.nearest_scope(declaration):

            return NameSource.Defined

        return NameSource.Adopted


class NameNodeGenerator(object):
    """Generates ast.Name nodes used for a given node.

    Surrogate ast.Name nodes will be given for names created by other actions
    such as function/class definitions and function parameters.

    This search does not recursively walk the ast. It only produces names which
    can be seen within the node given at initialization. For example, if the
    given node is a module that contains functions then the function names will
    be produced but not the names used within those functions (such as local
    variables or function parameters).
    """

    def __init__(self, node):

        self._node = node

    def __iter__(self):

        nodes = [self._node]
        while len(nodes) > 0:

            current = nodes.pop()
            for child in ast.iter_child_nodes(current):

                if isinstance(child, ast.Name):

                    yield child
                    continue

                if isinstance(child, ast.alias):

                    yield copy_location(
                        ast.Name(
                            id=(
                                child.asname
                                if child.asname is not None
                                else child.name
                            ),
                            ctx=ast.Store(),
                        ),
                        child,
                    )
                    continue

                if (
                    isinstance(child, ast.FunctionDef) or
                    isinstance(child, ast.ClassDef)
                ):

                    yield copy_location(
                        ast.Name(
                            id=child.name,
                            ctx=ast.Store(),
                        ),
                        child,
                    )
                    continue

                if isinstance(child, ast.Global):

                    for n in child.names:

                        yield copy_location(
                            ast.Name(
                                id=n,
                                ctx=ast.Store(),
                            ),
                            child,
                        )
                    continue

                if isinstance(child, ast.arguments):

                    if child.vararg is not None:

                        yield copy_location(
                            ast.Name(
                                id=child.vararg,
                                ctx=ast.Store(),
                            ),
                            child,
                        )

                    if child.kwarg is not None:

                        yield copy_location(
                            ast.Name(
                                id=child.kwarg,
                                ctx=ast.Store(),
                            ),
                            child,
                        )

                    # Not continuing on purpose.
                    # args and defaults may have Names.

                nodes.append(child)
