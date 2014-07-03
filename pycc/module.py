from collections import namedtuple
import os


ImportResult = namedtuple('ImportResult', ('module', 'target',))


class Package(object):
    """Contains AST nodes and metadata for modules in a Python package."""

    def __init__(self, location):

        self.location = os.path.realpath(location)
        self.root = os.path.split(self.location)[1]
        self._locations = {}
        self._paths = {}

    def _path_from_location(self, location):
        """Generate a Python path from a given disk location."""

        path = location.split(os.path.split(self.location)[0])[1]
        if path.endswith('__init__.py'):

            path = os.path.split(path)[0]

        # Strip the .py off the file to make a valid python path.
        if path.endswith('.py'):

            path = path[:-3]

        return path

    def add(self, location, node):
        """Add an AST module node for a given disk location."""

        location = os.path.realpath(location)

        if self.location not in location:

            raise ValueError("Module must be children of the root package.")

        path = self._path_from_location(location)
        mod = Module(
            location=location,
            path=path,
            node=node,
        )

        self._locations[location] = mod
        self._paths[path] = mod

    def modules(self):
        """Get a generator of Module objects in the package."""

        return self._paths.itervalues()

    def get(self, path):
        """Get the closest Module to an import path."""

        if '.' in path:

            path = path.replace('.', os.sep)

        if not path.startswith(os.sep):

            path = os.path.join(os.sep, path)

        if path in self._paths:

            return ImportResult(module=self._paths[path], target=None)

        path, target = os.path.split(path)

        if path not in self._paths:

            return None

        return ImportResult(module=self._paths[path], target=target)

    def __repr__(self):

        return '<Package {0} -- {1}>'.format(
            self.location,
            self.root,
        )


class Module(object):
    """Contains AST nodes and metadata for a single Python module."""

    __slots__ = (
        'path',
        'location',
        'node',
    )

    def __init__(self, location, path, node):

        self.location = location
        self.path = path
        self.node = node

    def __repr__(self):

        return '<Module {0} -- {1}>'.format(
            self.location,
            self.path,
        )
