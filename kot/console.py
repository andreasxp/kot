from typing import Optional
import click


_verbose = 0


def setverbose(verbose):
    global _verbose
    _verbose = verbose


def verbose():
    return _verbose


def echo(text=""):
    click.echo(str(text))


def log(text, good: Optional[bool] = None, wait=False):
    if good is None:
        color = "cyan"
    elif good:
        color = "green"
    else:
        color = "red"

    click.secho(str(text), nl=False, fg=color)

    if wait:
        input()
    else:
        print()


def error(text):
    click.secho(f"Error: {text}", fg="red")


def debug(text):
    if verbose():
        click.secho(str(text), fg="yellow")
