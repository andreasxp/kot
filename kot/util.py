import subprocess as sp
from pathlib import Path

from .console import log


def glob(pattern):
    """Glob files according to a pattern. Unlike pathlib.Path.glob, supports absolute paths."""
    pattern = Path(pattern)
    return (str(path) for path in Path(pattern.anchor).glob(str(pattern.relative_to(pattern.anchor))))


def interactive_execute(exe, pause=False):
    """Execute a process. Print exit code and optionally pause for user input in the end."""
    ret = sp.run(exe, check=False)
    log(f"\nProcess exited with code {ret.returncode}.", good=(ret.returncode == 0), wait=pause)
