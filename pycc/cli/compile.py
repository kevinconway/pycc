"""CLI tool for generating optimized .pyc files."""

import argparse
import ast
import marshal
import os
import py_compile
import time

from . import common
from .. import loader


def parse_args():

    parser = argparse.ArgumentParser(description='PyCC Compiler')
    parser = common.add_common_args(parser)
    parser.add_argument(
        '--destination',
        required=False,
        help='Path to place compiled binaries in.',
    )
    return parser.parse_args()


def make_pyc(module, destination):

    ast.fix_missing_locations(module.node)
    codeobject = compile(module.node, module.location, 'exec')

    destination_dir = os.path.split(destination)[0]

    if not os.path.exists(destination_dir):

        os.makedirs(destination_dir)

    with open(destination, 'wb') as pyc:
        pyc.write('\0\0\0\0')
        py_compile.wr_long(pyc, long(time.time()))
        marshal.dump(codeobject, pyc)
        pyc.flush()
        pyc.seek(0, 0)
        pyc.write(py_compile.MAGIC)


def main_module(path, optimizers, destination):

    mod = loader.ModuleLoader(path).load()

    for optimizer in optimizers:

        optimizer(mod, package=None)

    make_pyc(
        mod,
        os.path.join(
            destination,
            os.path.split(mod.location)[1] + 'c',
        ),
    )


def main_package(path, optimizers, destination):

    pkg = loader.PackageLoader(path).load()

    # Remove the trailing directory name if the compile directory is the same
    # as the source. This part of the name is provided by the python path when
    # joining the output_path to the destination.
    if pkg.location == destination:

        destination = os.path.split(destination)[0]

    for mod in pkg.modules():

        for optimizer in optimizers:

            optimizer(mod, package=pkg)

        output_path = mod.path + ".pyc"

        if mod.location.endswith('__init__.py'):

            output_path = os.path.join(mod.path, '__init__.pyc')

        if output_path.startswith(os.sep):

            output_path = output_path[1:]

        make_pyc(mod, os.path.join(destination, output_path))


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

    destination = os.path.realpath(
        os.path.expanduser(
            os.path.expandvars(
                args.destination
            )
        )
    ) if args.destination is not None else path

    if os.path.isfile(destination):

        destination = os.path.split(destination)[0]

    if not os.path.exists(destination):

        os.makedirs(destination)

    if os.path.isdir(path):

        main_package(path, optimizers, destination)

    else:

        main_module(path, optimizers, destination)


if __name__ == '__main__':

    main()
