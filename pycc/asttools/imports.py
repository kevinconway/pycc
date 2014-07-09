import ast
import os


def normalized_import(node, module):
    """Return an iterable of normalized paths for a given import statement.

    Paths are compatible with the module.Package.get() method.
    """

    if isinstance(node, ast.Import):

        return tuple(
            os.path.join('/', n.name.replace('.', '/'))
            for n in node.names
        )

    if isinstance(node, ast.ImportFrom):

        source_module = module.path if node.level > 0 else '/'
        for x in xrange(node.level):

            source_module = os.path.split(source_module)[0]

        return tuple(
            os.path.join(source_module, node.module, n.name)
            for n in node.names
        )

    raise ValueError("Node must be an import statement.")
