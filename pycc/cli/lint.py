"""CLI tool for detecting potentially problematic code."""

import argparse

from . import common


def parse_args():

    parser = argparse.ArgumentParser(description='PyCC Linter')
    parser = common.add_common_args(parser)
    return parser.parse_args()


def main():

    args = parse_args()

    collection = common.load_from_path(args.source)

    lint = []

    for item in collection:

        for bundle in common.bundles_from_args(args):

            lint.append((item, bundle[0](root=item.node).visit(item.node),))

    print

    for l in lint:

        if l[1]:

            print "{0}: ".format(l[0].file_path)

            for b in l[1]:

                print "line: {0}".format(b.lineno)

            print
            print


if __name__ == '__main__':

    main()
