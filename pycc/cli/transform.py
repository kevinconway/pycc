"""CLI tool for creating samples of optimized source code."""

import argparse

from astkit.render import SourceCodeRenderer

from . import common


def parse_args():

    parser = argparse.ArgumentParser(description='PyCC Transformer')
    parser = common.add_common_args(parser)
    return parser.parse_args()


def main():

    args = parse_args()

    collection = common.load_from_path(args.source)

    for item in collection:

        for bundle in common.bundles_from_args(args):

            found = bundle[0](root=item.node).visit(item.node)

            for transformer in bundle[1:]:

                tree = transformer(found).visit(item.node)

        print SourceCodeRenderer.render(tree)


if __name__ == '__main__':

    main()
