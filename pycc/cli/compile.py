"""CLI tool for generating optimized .pyc files."""

import argparse
import ast
import marshal
import os
import py_compile
import time
import tempfile

from astkit.render import SourceCodeRenderer

from . import common


def parse_args():

    parser = argparse.ArgumentParser(description='PyCC Compiler')
    parser = common.add_common_args(parser)
    parser.add_argument(
        '--destination',
        default='build',
        help='Path to place compiled binaries in.',
    )
    return parser.parse_args()

def pyc_direct(tree, ast_file, destination):

    codeobject = compile(tree, ast_file.file_path, 'exec')

    with open(destination, 'wb') as pyc:
        pyc.write('\0\0\0\0')
        py_compile.wr_long(pyc, long(time.time()))
        marshal.dump(codeobject, pyc)
        pyc.flush()
        pyc.seek(0, 0)
        pyc.write(py_compile.MAGIC)


def pyc_tmp_compile(tree, ast_file, destination):

    source = SourceCodeRenderer.render(tree)

    with tempfile.NamedTemporaryFile() as tmp:

        tmp.write(source)
        tmp.flush()

        py_compile.compile(tmp.name, destination)




def main():

    args = parse_args()

    collection = common.load_from_path(args.source)

    if not os.path.isdir(args.destination):

        os.makedirs(args.destination)

    for item in collection:

        for bundle in common.bundles_from_args(args):

            found = bundle[0](root=item.node).visit(item.node)

            for transformer in bundle[1:]:

                tree = transformer(found).visit(item.node)

        ast.fix_missing_locations(tree)
        output_path = os.path.join(
            args.destination,
            item.python_path or os.path.split(item.file_path)[1] + "c",
        )
        pyc_tmp_compile(tree, item, output_path)


if __name__ == '__main__':

    main()
