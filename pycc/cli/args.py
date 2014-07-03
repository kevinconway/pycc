def register_constants(parser):

    parser.add_argument(
        '--constants',
        help="Replace constant expresions with inline literals.",
        action='store_const',
        default=None,
        const="pycc_constant_inliner",
    )
