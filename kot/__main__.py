import sys

import kot

from kot.cli import parser, cli_build, cli_run, cli_launch
from kot.console import error as log_error
from kot.console import log
from kot.update import prompt_to_update


def main():
    __excepthook__ = sys.excepthook

    def excepthook(etype, value, tb):
        if isinstance(value, KeyboardInterrupt):
            log("\nReceived keyboard interrupt.", good=False)
            sys.exit(3)
        else:
            __excepthook__(etype, value, tb)

    sys.excepthook = excepthook

    args = parser.parse_args()
    if args.subcommand == "build":
        if args.verbose:
            kot.print_debug = True

        cli_action = cli_build
    elif args.subcommand == "run":
        if args.verbose:
            kot.debug_mode = True

        cli_action = cli_run
    elif args.subcommand == "launch":
        if args.verbose:
            kot.debug_mode = True

        cli_action = cli_launch
    else:
        parser.error("missing subcommand")

    result = 0
    try:
        cli_action(args)
    except kot.BuildSystemError as e:
        log_error(e)
        result = 2
    except kot.BuildFailure as e:
        log_error(e)
        result = 1

    prompt_to_update()

    return result


if __name__ == "__main__":
    sys.exit(main())
