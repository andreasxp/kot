import os
import shlex
import shutil
import subprocess as sp
from argparse import REMAINDER, ArgumentParser
from itertools import chain
from os.path import isfile, expandvars
from pathlib import Path

import kot

from .base import build, config, launch
from .console import log, debug as log_debug
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

    command = [cli_build(cli)]
    if cli.args is not None:
        command += shlex.split(cli.args)

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


def cli_playground(cli):
    playgrounddir = kot.datadir + "/playground"
    Path(playgrounddir).mkdir(exist_ok=True)

    playgroundfile = playgrounddir + "/source.cpp"
    if not isfile(playgroundfile):
        shutil.copyfile(kot.rootdir + "/data/playground_template.cpp", playgroundfile)

    os.environ["playground"] = playgroundfile
    editorargs = shlex.split(config["command.editor"])
    editorargs = [expandvars(arg) for arg in editorargs]
    editorargs = [arg.replace("\\", "/") for arg in editorargs]

    log_debug(f"Editor process: {editorargs}")
    ret = sp.run(editorargs, env=os.environ, check=False).returncode

    if ret != 0:
        raise kot.EditorError(f"Editor process crashed with code {ret}.")

    with open(playgroundfile, "r", encoding="utf-8") as f:
        code = f.read()

    log("Source code")
    print(code)

    if cli.terminal:
        # Print helpful messages to separate source code, building and running
        # cli_run prints this only when not cli.terminal, but we need this regardless of style to separarate compilation
        # from source code
        log("Building")

    cli.file = [playgroundfile]
    cli.debug = False
    cli.output = kot.tempdir + "/playground.exe"
    cli.args = None

    cli_run(cli)


def cli_config(cli):
    value = shlex.join(cli.value)

    try:
        if value != "":
            config[cli.name] = value
        print(config[cli.name])
    except KeyError:
        raise kot.MissingConfigEntryError(f"No config entry for \"{cli.name}\"") from None


# Argument parser ======================================================================================================
def _make_parser():
    parser = ArgumentParser("kot", description="A very simple C++ builder and runner.")
    parser.set_defaults(subcommand=None)
    parser.add_argument("-V", "--version", action='version', version=kot.__version__)
    parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
    subparsers = parser.add_subparsers(title="subcommands")

    subparser = subparsers.add_parser("build", description="Build a C++ file.")
    subparser.set_defaults(subcommand="build")
    subparser.add_argument("file", nargs="+", help="one or more .cpp files to build")
    subparser.add_argument("-d", "--debug", action="store_true", help="build in debug mode")
    subparser.add_argument("-o", "--output", help="specify a different name for the output file")

    subparser = subparsers.add_parser("run", description="Run a C++ file, compiling it first.")
    subparser.set_defaults(subcommand="run")
    subparser.add_argument("file", nargs="+", help="one or more .cpp files to build or a single binary file to run")
    subparser.add_argument("-d", "--debug", action="store_true", help="build in debug mode")
    subparser.add_argument("-o", "--output", help="specify a different name for the output file")
    subparser.add_argument("--args", help="cli arguments for execution")
    stylegroup = subparser.add_mutually_exclusive_group()
    stylegroup.add_argument("-p", "--pause", action="store_true", help="pause after executing")
    stylegroup.add_argument("-t", "--terminal", action="store_true", help="run in a separate terminal and pause")

    subparser = subparsers.add_parser("launch", description="Launch a binary executable.")
    subparser.set_defaults(subcommand="launch")
    subparser.add_argument("command", nargs=REMAINDER, help="executable and arguments to launch")
    stylegroup = subparser.add_mutually_exclusive_group()
    stylegroup.add_argument("-p", "--pause", action="store_true", help="pause after executing")
    stylegroup.add_argument("-t", "--terminal", action="store_true", help="run in a separate terminal and pause")

    subparser = subparsers.add_parser("pg", description="Launch code from an interactive playground.")
    subparser.set_defaults(subcommand="pg")
    stylegroup = subparser.add_mutually_exclusive_group()
    stylegroup.add_argument("-p", "--pause", action="store_true", help="pause after executing")
    stylegroup.add_argument("-t", "--terminal", action="store_true", help="run in a separate terminal and pause")

    subparser = subparsers.add_parser("config", description="Configure kot behavior.")
    subparser.set_defaults(subcommand="config")
    subparser.add_argument("name", help="Configuration entry to view or configure")
    subparser.add_argument("value", nargs=REMAINDER, help="Optional new value for the config entry.")

    return parser


parser = _make_parser()

cli_handlers = {
    "build": cli_build,
    "run": cli_run,
    "launch": cli_launch,
    "pg": cli_playground,
    "config": cli_config
}
