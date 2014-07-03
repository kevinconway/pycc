"""CLI tool for creating samples of optimized source code."""

import argparse
import os

from astkit.render import SourceCodeRenderer

from . import common
from .. import loader


def parse_args():

    parser = argparse.ArgumentParser(description='PyCC Transformer')
    parser = common.add_common_args(parser)
    return parser.parse_args()


def main_module(path, optimizers):

    mod = loader.ModuleLoader(path).load()

    for optimizer in optimizers:
        optimizer(mod, package=None)

    print SourceCodeRenderer.render(mod.node)


def main_package(path, optimizers):

    pkg = loader.PackageLoader(path).load()

    for mod in pkg.modules():
        for optimizer in optimizers:
            optimizer(mod, package=pkg)

        print SourceCodeRenderer.render(mod.node)


def main():

    args = parse_args()

    optimizers = common.optimizers_from_args(args)

    path = os.path.realpath(
        os.path.expanduser(
            os.path.expandvars(
                args.source
            )
        )
    )

    if os.path.isdir(path):

        main_package(path, optimizers)

    else:

        main_module(path, optimizers)


if __name__ == '__main__':

    main()
