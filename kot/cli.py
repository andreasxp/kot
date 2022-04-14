import subprocess as sp
import sys
from itertools import chain
from pathlib import Path

import kot

from .build import build_vs
from .console import log
from .util import glob, interactive_execute


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

    returncode = build_vs(sources, output, debug)

    if returncode != 0:
        raise kot.BuildFailure(f"Compilation failed with code {returncode}.")

    return output


def cli_run(cli):
    """Run a binary, optionally compiling it from sources first."""
    if cli.binary:
        exe = cli.file[0]
    else:
        if not cli.terminal:
            # Print helpful messages to separate building and running
            log("Building")

        exe = cli_build(cli)

        if not cli.terminal:
            # Print helpful messages to separate building and running
            log("Launching")

    if cli.terminal:
        if sys.executable.endswith("kot.exe"):
            wrapper_executable = [sys.executable]
        else:
            wrapper_executable = [sys.executable, kot.rootdir + "/__main__.py"]

        sp.run(wrapper_executable + ["run", "-bp", exe], creationflags=sp.CREATE_NEW_CONSOLE, check=False)
    else:
        interactive_execute(exe, cli.pause)
