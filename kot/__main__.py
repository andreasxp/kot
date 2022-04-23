import sys

import click

import kot
from kot.cli import cli
from kot.console import error as log_error
from kot.console import log
from kot.update import prompt_to_update


def main():
    try:
        cli.main(standalone_mode=False)
    except (kot.BuildFailure, kot.MissingConfigEntryError) as e:
        log_error(e)
        return 1
    except (kot.BuildSystemError, kot.EditorError) as e:
        log_error(e)
        return 2
    except click.exceptions.Abort:
        log("\nAborted.", good=False)
        return 3

    prompt_to_update()


if __name__ == "__main__":
    sys.exit(main())
