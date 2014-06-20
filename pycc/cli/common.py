"""Common utilities for CLI modules"""

import os

from ..asttools import load
from ..visitors import constants
from ..visitors import forlist
from ..visitors import rangelen
from ..visitors import reversedrange


def add_common_args(parser):
    """Add arguments required for all CLI tools."""

    parser.add_argument(
        'source',
        help='Path to the python source code. May be file or directory.',
    )

    parser.add_argument(
        '--constants',
        help="Replace constant expresions with inline literals.",
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '--forlist',
        help="Replace loops over inline lists with xrange.",
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '--rangelen',
        help="Replace range(len()) index loops with iter loops..",
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '--reversedrange',
        help="Replace range(len()-1, -1, -1) index loops with revesed()..",
        action='store_true',
        default=False,
    )

    return parser


def bundles_from_args(args):
    """Return a list of tuples containing check/transform bundles.

    The first element of a bundle is the checker. All other elements are
    transformers.
    """

    bundles = []

    if args.constants:

        bundles.append((constants.ConstantFinder, constants.ConstantInliner))

    if args.forlist:

        bundles.append((forlist.ForListFinder, forlist.XRangeReplacer))

    if args.rangelen:

        bundles.append((rangelen.RangeLenFinder, rangelen.IterLoopReplacer))

    if args.reversedrange:

        bundles.append((
            reversedrange.ReversedRangeFinder,
            reversedrange.ReversedIterReplacer,
        ))

    return bundles


def load_from_path(path):
    """Return an iterable of AstFile objects using the asttools loaders."""

    if os.path.isdir(path):

        return load.load_directory(path)

    return [load.load_file(path)]
