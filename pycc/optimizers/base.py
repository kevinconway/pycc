"""Interfaces for the Finder and Optimizer."""

from collections import namedtuple


FinderResult = namedtuple('FinderResult', ('node', 'module', 'package'))


class Base(object):

    def __init__(self, module, package=None):

        self.module = module
        self.package = package


class Finder(Base):
    """Detects unoptimized code."""

    def __call__(self):
        """Generate an iterable of FinderResult."""

        raise NotImplementedError()


class Transformer(Base):
    """Transforms and optimizes code."""

    def __call__(self, found):
        """Run this optimizer on the given FinderResult."""

        raise NotImplementedError()


class Check(Base):
    """Checks for some artifact in the code."""

    def __call__(self):
        """Return true/false if artifact is detected/undetected."""

        raise NotImplementedError()
