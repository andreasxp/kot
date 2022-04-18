import atexit
import shutil
from os.path import dirname
from pathlib import Path
from tempfile import mkdtemp

import appdirs

__version__ = "0.3.1"

rootdir = dirname(__file__).replace("\\", "/")
tempdir = mkdtemp().replace("\\", "/")
configdir = appdirs.user_config_dir("kot", appauthor=False, roaming=True).replace("\\", "/")
datadir = appdirs.user_data_dir("kot", appauthor=False, roaming=True).replace("\\", "/")

Path(configdir).mkdir(parents=True, exist_ok=True)
Path(datadir).mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(tempdir))


class KotError(Exception):
    """Base class for all exceptions raised by kot."""


class MissingConfigEntryError(KotError):
    """Config entry is missing."""


class EditorError(KotError):
    """Editor process crashed."""


class BuildSystemError(KotError):
    """Build system is broken."""


class BuildFailure(KotError):
    """Build system attempted to build, but failed due to errors in source files."""
