import sys

import click

import kot
from kot import console
from kot.cli import cli
from kot.update import prompt_to_update


def main():
    try:
        cli.main(standalone_mode=False)
        result = 0
    except (kot.BuildFailure, kot.MissingConfigEntryError) as e:
        click.echo()
        console.error(e)
        result = 1
    except (kot.BuildSystemError, kot.EditorError) as e:
        console.echo()
        console.error(e)
        result = 2
    except click.exceptions.Abort:
        console.log("\nAborted.", good=False)
        result = 3
    except click.exceptions.UsageError as e:
        console.echo(e.ctx.get_usage() + "\n")
        console.error(e.format_message())
        result = 4
    except click.exceptions.ClickException as e:
        e.show()
        result = -1

    prompt_to_update()
    return result


if __name__ == "__main__":
    sys.exit(main())
