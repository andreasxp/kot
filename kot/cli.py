from itertools import chain
from pathlib import Path
from argparse import ArgumentParser, REMAINDER

import kot

from .base import build, launch
from .console import log
from .util import glob


def sources_from_cli(sources):
    """Convert a list of sources as specified by the user to a list of sources ready for compilation.
    Resolves glob patterns and ~ symbols.
    """
    expanded_sources = (Path(source).expanduser() for source in sources)
    globbed_sources = (glob(pattern) for pattern in expanded_sources)
    result = list(chain.from_iterable(globbed_sources))

    return result


def output_from_cli(sources, override=None):
    """Calculate output path. Usually it's sources[0] with an `.exe` suffix. If override is not None, use override."""
    default_name = "app"

    if override is not None:
        result = Path(override)
        if result.suffix != ".exe":
            result = Path(str(result) + ".exe")
    elif len(sources) > 1 or "*" in sources[0]:
        result = Path(default_name + ".exe")
    else:
        result = Path(sources[0]).with_suffix(".exe")

    result = result.expanduser()
    return str(result)


def cli_build(cli):
    sources = sources_from_cli(cli.file)
    output = output_from_cli(sources, cli.output)
    debug = cli.debug

    returncode = build(sources, output, debug)

    if returncode != 0:
        raise kot.BuildFailure(f"Compilation failed with code {returncode}.")

    return output


def cli_launch(cli):
    command = cli.command

    if cli.terminal:
        style = "terminal"
    elif cli.pause:
        style = "pause"
    else:
        style = None

    launch(command, style=style)


def cli_run(cli):
    """Run a binary, optionally compiling it from sources first."""
    # Build ------------------------------------------------------------------------------------------------------------
    if not cli.terminal:
        # Print helpful messages to separate building and running
        log("Building")

    command = cli_build(cli)

    if not cli.terminal:
        # Print helpful messages to separate building and running
        log("Launching")

    # Launch -----------------------------------------------------------------------------------------------------------
    if cli.terminal:
        style = "terminal"
    elif cli.pause:
        style = "pause"
    else:
        style = None

    launch(command, style=style)


# Argument parser ======================================================================================================
def _make_parser():
    parser = ArgumentParser("kot", description="A very simple C++ builder and runner.")
    parser.set_defaults(subcommand=None)
    parser.add_argument("-V", "--version", action='version', version=kot.__version__)
    subparsers = parser.add_subparsers(title="subcommands")

    parser_build = subparsers.add_parser("build", description="Build a C++ file.")
    parser_build.set_defaults(subcommand="build")
    parser_build.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
    parser_build.add_argument("-d", "--debug", action="store_true", help="build in debug mode")
    parser_build.add_argument("-o", "--output", help="specify a different name for the output file")
    parser_build.add_argument("file", nargs="+", help="one or more .cpp files to build")

    parser_run = subparsers.add_parser("run", description="Run a C++ file, compiling it first.")
    parser_run.set_defaults(subcommand="run")
    parser_run.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
    parser_run.add_argument("-d", "--debug", action="store_true", help="build in debug mode")
    parser_run.add_argument("-o", "--output", help="specify a different name for the output file")
    style = parser_run.add_mutually_exclusive_group()
    style.add_argument("-p", "--pause", action="store_true", help="pause after executing")
    style.add_argument("-t", "--terminal", action="store_true", help="run in a separate terminal and pause")
    parser_run.add_argument("file", nargs="+", help="one or more .cpp files to build or a single binary file to run")

    parser_run = subparsers.add_parser("launch", description="Launch a binary executable.")
    parser_run.set_defaults(subcommand="launch")
    parser_run.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
    style = parser_run.add_mutually_exclusive_group()
    style.add_argument("-p", "--pause", action="store_true", help="pause after executing")
    style.add_argument("-t", "--terminal", action="store_true", help="run in a separate terminal and pause")
    parser_run.add_argument("command", nargs=REMAINDER, help="executable and arguments to launch")

    return parser


parser = _make_parser()
