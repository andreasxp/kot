import json
import shutil
import subprocess as sp
import sys
from collections.abc import MutableMapping, Iterable
from os.path import expanduser, expandvars

import kot
from kot import console


def build(sources: Iterable[str], output: str, debug: bool):
    """Build an executable from a list of sources. Use Visual Studio compiler."""
    sources = list(sources)
    output = str(output)

    # Find Visual Studio compiler --------------------------------------------------------------------------------------
    if shutil.which("cl") is None:
        vswhere_path = kot.rootdir + "/data/vswhere.exe"
        ret = sp.run([vswhere_path, "-property", "InstallationPath"], text=True, capture_output=True, check=True)

        if ret.stdout == "":
            raise kot.BuildSystemError("Could not find Visual Studio.")

        vspath = ret.stdout[:-1]

        activate_environment = [
            "import-module", f"\"{vspath}/Common7/Tools/Microsoft.VisualStudio.DevShell.dll\"", ";",
            "Enter-VsDevShell", "-VsInstallPath", f"\"{vspath}\"", "-SkipAutomaticLocation",
            "-DevCmdArguments", "'-arch=x64 -no_logo'", ";"
        ]
    else:
        activate_environment = None

    compiler = ["cl"]
    if len(sources) == 0:
        raise kot.BuildSystemError("no source files with specified names found.")

    # Collect build args -----------------------------------------------------------------------------------------------
    target_args = ["/Fe:", output]
    misc_args = ["/std:c++latest", "/W3", "/nologo", "/EHsc", "/Zc:preprocessor", "/Fo:", kot.tempdir + "\\"]
    optimization_args = [
        "/Od" if debug else "/O2",
        "/MTd" if debug else "/MT"
    ]
    include_args = []
    link_args = []

    # Include vcpkg if scecified
    vcpkg_dir = config["path.vcpkg"]
    if vcpkg_dir:
        vcpkg_dir = expandvars(expanduser(vcpkg_dir)).replace("\\", "/")
        vcpkg_include_dir = vcpkg_dir + "/installed/x64-windows-static/include"
        vcpkg_lib_dir = vcpkg_dir + "/installed/x64-windows-static/lib"

        include_args = ["/I", vcpkg_include_dir]
        link_args = ["/link", f"/LIBPATH:\"{vcpkg_lib_dir}\""]

    args = compiler + sources + target_args + misc_args + optimization_args + include_args + link_args
    args = [str(arg) for arg in args]
    console.debug(f"Compiling: {' '.join(args)}")

    # Build ------------------------------------------------------------------------------------------------------------
    if activate_environment is None:
        ret = sp.run(args, check=False)
    else:
        ret = sp.run(activate_environment + args, shell=True, executable=shutil.which("powershell"), check=False)

    if ret.returncode != 0:
        raise kot.BuildFailure(f"Compilation failed with code {ret.returncode}.")


def launch(command: Iterable[str], presentation: str):
    command = list(command)

    if presentation == "terminal":
        if sys.executable.endswith("kot.exe"):
            wrapper_executable = [sys.executable]
        else:
            wrapper_executable = [sys.executable, kot.rootdir + "/__main__.py"]

        sp.run(wrapper_executable + ["launch", "-p"] + command, creationflags=sp.CREATE_NEW_CONSOLE, check=True)
    else:
        ret = sp.run(command, check=False)
        console.log(f"\nProcess exited with code {ret.returncode}.", good=(
            ret.returncode == 0), wait=(presentation == "pause"))


class Config(MutableMapping):
    @classmethod
    def _configpath(cls):
        return kot.configdir + "/config.json"

    @classmethod
    def _load(cls):
        configpath = cls._configpath()
        try:
            with open(configpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "command": {
                    "editor": r"notepad.exe $playground",
                },
                "path": {
                    "vcpkg": None,
                }
            }

    @classmethod
    def _save(cls, config):
        configpath = cls._configpath()
        with open(configpath, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent="\t")

    def __getitem__(self, key):
        config = self._load()

        key = key.split(".")
        value = config
        for part in key:
            value = value[part]

        return value

    def __setitem__(self, key, value):
        config = self._load()

        parts = key.split(".")
        nestedconfig = config
        for part in parts[:-1]:
            nestedconfig = nestedconfig[part]
        finalkey = parts[-1]

        if finalkey not in nestedconfig:
            raise KeyError(f"config entry {key} does not exist")

        nestedconfig[finalkey] = value
        self._save(config)

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        config = self._load()
        return iter(config)

    def __len__(self):
        config = self._load()
        return len(config)


config = Config()
