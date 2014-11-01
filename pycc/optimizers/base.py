"""Standard interfaces for optimizers."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class Optimizer(object):

    """Transforms and optimizes an AST node in place."""

    def __call__(self, node):
        """Modify the given AST node to optimize performance."""
        raise NotImplementedError()
