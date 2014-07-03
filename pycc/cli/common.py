"""Common utilities for CLI modules"""

from pkg_resources import iter_entry_points


def add_common_args(parser):
    """Add arguments required for all CLI tools."""

    parser.add_argument(
        'source',
        help='Path to the python source code. May be file or directory.',
    )

    for registration in iter_entry_points('pycc.cli.args'):

        registration.load()(parser)

    return parser


def optimizers_from_args(args):
    """Return an iterable of optimizer functions."""

    optimizers = []

    argd = args.__dict__
    for arg in argd:

        if hasattr(argd[arg], 'startswith') and argd[arg].startswith('pycc_'):

            for optimizer in iter_entry_points('pycc.optimizers', argd[arg]):

                optimizers.append(optimizer.load())
                break

            else:

                raise ImportError(
                    "Could not load optimizer plugin named {0}.".format(
                        argd[arg],
                    )
                )

    return optimizers
