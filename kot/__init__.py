from os.path import dirname

__version__ = "0.2.1"

rootdir = dirname(__file__)
debug_mode = False


class BuildSystemError(RuntimeError):
    """Build system is broken."""


class BuildFailure(ValueError):
    """Build system attempted to build, but failed due to errors in source files."""
