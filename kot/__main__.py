import sys

import kot

from kot.cli import parser, cli_handlers
from kot.console import error as log_error
from kot.console import log, setverbose
from kot.update import prompt_to_update


def main():
    __excepthook__ = sys.excepthook

    def excepthook(etype, value, tb):
        if isinstance(value, (kot.BuildFailure, kot.MissingConfigEntryError)):
            log_error(value)
            sys.exit(1)
        elif isinstance(value, (kot.BuildSystemError, kot.EditorError)):
            log_error(value)
            sys.exit(2)
        elif isinstance(value, KeyboardInterrupt):
            log("\nReceived keyboard interrupt.", good=False)
            sys.exit(3)
        elif isinstance(value, kot.KotError):
            log_error(value)
            sys.exit(-1)
        else:
            __excepthook__(etype, value, tb)

        prompt_to_update()

    sys.excepthook = excepthook

    args = parser.parse_args()
    try:
        handler = cli_handlers[args.subcommand]
    except KeyError:
        if args.subcommand is None:
            parser.error("missing subcommand")
        else:
            parser.error(f"unknown subcommand: {args.subcommand}")

    setverbose(int(args.verbose))
    handler(args)
    prompt_to_update()


if __name__ == "__main__":
    sys.exit(main())
