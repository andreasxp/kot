import atexit
import shutil
import subprocess as sp
from os.path import expanduser
from tempfile import mkdtemp

import kot

from .console import debug as log_debug

include_dir = expanduser("~/vcpkg/installed/x64-windows-static/include")
lib_dir = expanduser("~/vcpkg/installed/x64-windows-static/lib")
print_debug = False


def build_vs(sources: list, output: str, debug: bool):
    """Build an executable from a list of sources. Use Visual Studio compiler."""

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
        raise kot.BuildSystemError("No source files with specified names found.")

    # Create temp directory for compilation ----------------------------------------------------------------------------
    temp_dir = mkdtemp()
    atexit.register(lambda: shutil.rmtree(temp_dir))

    # Collect build args -----------------------------------------------------------------------------------------------
    target_args = ["/Fe:", output]
    misc_args = ["/std:c++latest", "/W3", "/nologo", "/EHsc", "/Zc:preprocessor", "/Fo:", temp_dir + "\\"]
    optimization_args = [
        "/Od" if debug else "/O2",
        "/MTd" if debug else "/MT"
    ]
    include_args = ["/I", include_dir]
    link_args = ["/link", f"/LIBPATH:\"{lib_dir}\""]

    args = compiler + sources + target_args + misc_args + optimization_args + include_args + link_args
    args = [str(arg) for arg in args]
    log_debug(f"Compiling: {' '.join(args)}")

    # Build ------------------------------------------------------------------------------------------------------------
    if activate_environment is None:
        ret = sp.run(args, check=False)
    else:
        ret = sp.run(activate_environment + args, shell=True, executable=shutil.which("powershell"), check=False)

    return ret.returncode
