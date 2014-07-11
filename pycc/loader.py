"""Objects that load files into Module and Package objects."""

import os

from .asttools import parse
from .module import Package


class ModuleLoader(object):
    """Loader for a single Python module."""

    def __init__(self, path):

        path = os.path.realpath(path)
        if not path.endswith('.py'):

            raise ValueError(
                "Path {0} is not a Python module.".format(path),
            )

        self.path = path

    def load(self):
        """Create a Module from the given path."""

        code = ""
        with open(self.path, 'r') as f:

            code = f.read()

        node = parse.parse(code, filename=self.path, mode='exec')

        return Package(self.path).add(self.path, node)

    def __repr__(self):

        return '<ModuleLoader {0}>'.format(self.path)


class PackageLoader(object):
    """Loader for a Python package directory."""

    def __init__(self, path):

        path = os.path.realpath(path)
        if '__init__.py' not in os.listdir(path):

            raise ValueError(
                "Path ({0}) is not a Python package.".format(path),
            )

        self.path = path

    def load(self):
        """Create a Package from a given path."""

        collection = Package(self.path)

        directories = [self.path]

        while directories:

            cwd = directories.pop()

            for item in os.listdir(cwd):

                item = os.path.realpath(os.path.join(cwd, item))

                if os.path.isdir(item):

                    directories.append(item)

                if not os.path.isdir(item) and item.endswith('.py'):

                    collection.add(
                        location=item,
                        node=ModuleLoader(path=item).load().node
                    )

        return collection

    def __repr__(self):

        return '<PackageLoader {0}>'.format(self.path)
