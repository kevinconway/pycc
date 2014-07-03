"""Common utilities for CLI modules"""

from ..optimizers import constant


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

    return parser


def optimizers_from_args(args):
    """Return an iterable of optimizer functions."""

    optimizers = []

    if args.constants:

        optimizers.append(constant.optimize)

    return optimizers
