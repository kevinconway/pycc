import ast


class NodeFinder(ast.NodeVisitor):
    """Visitor that returns an iterable of problematic nodes."""

    def __init__(self, root):

        self.root = root
        self._results = []

    def visit(self, node):

        super(NodeFinder, self).visit(node)
        return self._results[:]

    def add(self, node):
        """Add a problematic node to the results output."""

        self._results.append(node)
