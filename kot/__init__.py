import atexit
import shutil
from os.path import dirname
from pathlib import Path
from tempfile import mkdtemp

import appdirs

__version__ = "0.2.1"

rootdir = dirname(__file__)
tempdir = mkdtemp()
configdir = appdirs.user_config_dir("kot", appauthor=False, roaming=True)
datadir = appdirs.user_data_dir("kot", appauthor=False, roaming=True)

Path(configdir).mkdir(parents=True, exist_ok=True)
Path(datadir).mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(tempdir))

debug_mode = False


class EditorError(RuntimeError):
    """Editor process crashed."""


class BuildSystemError(RuntimeError):
    """Build system is broken."""


class BuildFailure(ValueError):
    """Build system attempted to build, but failed due to errors in source files."""
