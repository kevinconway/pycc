def register(parser):

    parser.add_argument(
        '--constants',
        help="Replace constant expressions with inline literals.",
        action='store_const',
        default=None,
        const="pycc_constant_inliner",
    )
