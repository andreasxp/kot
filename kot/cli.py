import os
import shlex
import shutil
import subprocess as sp
from os.path import isfile, expandvars
from pathlib import Path
import click

import kot

from kot import base
from .console import log, debug as log_debug, setverbose


def _output_callback(ctx, param, value):
    """Compute final executable name."""
    # Sources are guaranteed to exist if value is None
    # See https://click.palletsprojects.com/en/8.1.x/advanced/?highlight=callback#callback-evaluation-order
    sources = ctx.params.get("sources", [])

    if value:
        # If specified in CLI, use that, with .exe suffix if missing
        if Path(value).suffix != ".exe":
            value = value + ".exe"
    elif len(sources) == 1:
        # If just one source, use source filename with .exe suffix
        value = str(Path(Path(sources[0]).name).with_suffix(".exe"))
    else:
        # Otherwise use default name
        value = "app.exe"

    return value


def _build_options(f):
    sources = click.argument("sources", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
                             required=True, nargs=-1)
    output = click.option("-o", "--output", type=click.Path(file_okay=True, dir_okay=False, writable=True),
                          help="Output filename.", show_default="source name or 'app' for many sources",
                          callback=_output_callback)
    buildmode = click.option("--debug/--release", "-d/-r", default=False, help="Building mode.", show_default=True)

    return sources(output(buildmode(f)))


def _presentation_options(f):
    pause = click.option("-p", "--pause", "presentation", flag_value="pause", help="Pause after execution.")
    terminal = click.option("-t", "--terminal", "presentation", flag_value="terminal",
                            help="Open a separate terminal for output and pause after execution.")

    return pause(terminal(f))


@click.group(help="A very simple C++ builder and runner.", context_settings=dict(max_content_width=200))
@click.option("-v", "verbose", is_eager=True, is_flag=True, default=False, expose_value=False,
              help="Enable verbose output.", callback=lambda ctx, param, verbose: setverbose(verbose))
@click.version_option(kot.__version__, prog_name="Kot", message="%(prog)s %(version)s")
def cli():
    pass


@cli.command()
@_build_options
def build(sources, output, debug):
    """Build a binary from C++ source files."""
    returncode = base.build(sources, output, debug)

    if returncode != 0:
        raise kot.BuildFailure(f"Compilation failed with code {returncode}.")


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False))
@click.argument("command", type=click.UNPROCESSED, required=True, nargs=-1)
@_presentation_options
def launch(command, presentation):
    """Execute any command and print exit code."""
    base.launch(command, presentation)


@cli.command()
@_build_options
@_presentation_options
@click.option("--args", type=click.UNPROCESSED, default="", help="Additional cli arguments for the executable.")
def run(sources, output, debug, presentation, args):
    """Build and run a binary from C++ source files."""
    if presentation != "terminal":
        # Print helpful messages to separate building and running
        log("Building")

    base.build(sources, output, debug)

    if presentation != "terminal":
        # Print helpful messages to separate building and running
        log("Launching")

    base.launch([output] + shlex.split(args), presentation)


@cli.command()
@_presentation_options
def pg(presentation):
    """Open an interactive C++ playground."""
    playgrounddir = kot.datadir + "/playground"
    Path(playgrounddir).mkdir(exist_ok=True)

    playgroundfile = playgrounddir + "/source.cpp"
    if not isfile(playgroundfile):
        shutil.copyfile(kot.rootdir + "/data/playground_template.cpp", playgroundfile)

    os.environ["playground"] = playgroundfile
    editorargs = shlex.split(base.config["command.editor"])
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

    output = kot.tempdir + "/playground.exe"

    log("Building")
    base.build([playgroundfile], output, debug=False)

    if presentation != "terminal":
        # Print helpful messages to separate building and running
        log("Launching")

    base.launch([output], presentation)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False))
@click.argument("name", required=True)
@click.argument("value", type=click.UNPROCESSED, nargs=-1)
def config(name, value):
    """View config entry 'name' or replace it with 'value', if specified."""
    if name.startswith("command"):
        value = shlex.join(value)
    else:
        value = " ".join(value)

    try:
        if value != "":
            base.config[name] = value
        print(base.config[name])
    except KeyError:
        raise kot.MissingConfigEntryError(f"No config entry for \"{name}\"") from None
