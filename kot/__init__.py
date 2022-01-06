import atexit
import shutil
import subprocess as sp
import sys
from argparse import ArgumentParser
from itertools import chain
from pathlib import Path
from tempfile import mkdtemp

from colorama import init as colorama_init, Fore, Style

__version__ = "0.1.0"

dir = Path(__file__).parent
temp_dir = mkdtemp()
include_dir = Path("~/vcpkg/installed/x64-windows-static/include").expanduser()
lib_dir = Path("~/vcpkg/installed/x64-windows-static/lib").expanduser()
vswhere_path = dir / "data" / "vswhere.exe"


def coloprint(*args, **kwargs):
    colorama_init(autoreset=True)
    print(*args, **kwargs)

def glob(pattern):
    """Glob files according to a pattern. Unlike pathlib.Path.glob, supports absolute paths."""
    pattern = Path(pattern)

    return Path(pattern.anchor).glob(str(pattern.relative_to(pattern.anchor)))

def output_name(sources, override=None):
    """Calculate output path. Usually it's sources[0] with an `.exe` suffix. If override is not None, use override."""
    default_name = "app"

    if override is not None:
        result = Path(override).expanduser()
        if result.suffix != ".exe":
            result += ".exe"
        return result

    if len(sources) > 1 or "*" in sources[0]:
        return default_name + ".exe"

    return Path(sources[0]).stem + ".exe"


def process_sources(sources):
    """Convert a list of sources as specified by the user to a list of sources ready for compilation.
    Resolves glob patterns and ~ symbols.
    """
    expanded_sources = (Path(source).expanduser() for source in sources)
    globbed_sources = (glob(pattern) for pattern in expanded_sources)
    flat_globbed_sources = chain.from_iterable(globbed_sources)
    result = [str(source) for source in flat_globbed_sources]

    return result


def interactive_execute(exe, pause=False):
    """Execute something. Pring exit code and optionally pause for user input in the end."""
    ret = sp.run(exe, check=False)

    if ret.returncode == 0:
        color = Style.BRIGHT + Fore.GREEN
    else:
        color = Style.BRIGHT + Fore.RED

    coloprint(f"\n{color}Process exited with code {ret.returncode}.", end="")

    if pause:
        input()
    else:
        print()


def build(sources, debug, output):
    """Build an executable from a list of sources. Currently only cl.exe is supported."""
    # Determine compiler
    cl_location = shutil.which("cl")
    if cl_location is None:
        ret = sp.run([vswhere_path, "-property", "InstallationPath"], text=True, capture_output=True, check=True)

        if ret.stdout == "":
            coloprint(f"{Style.BRIGHT}{Fore.RED}Error: Could not find Visual Studio.")
            sys.exit(1)
        else:
            vspath = ret.stdout[:-1]

        activate_environment = [
            "import-module", f"\"{vspath}/Common7/Tools/Microsoft.VisualStudio.DevShell.dll\"", ";",
            "Enter-VsDevShell", "-VsInstallPath", f"\"{vspath}\"", "-SkipAutomaticLocation",
            "-DevCmdArguments", "'-arch=x64 -no_logo'", ";"
        ]
    else:
        activate_environment = None


    compiler = ["cl"]
    sources_args = process_sources(sources)
    target_args = ["/Fe:", output_name(sources, output)]
    misc_args = ["/std:c++latest", "/W3", "/nologo", "/EHsc", "/Zc:preprocessor", "/Fo:", temp_dir + "\\"]
    optimization_args = [
        "/Od" if debug else "/O2",
        "/MTd" if debug else "/MT"
    ]
    include_args = ["/I", str(include_dir)]
    link_args = ["/link", f"/LIBPATH:\"{lib_dir}\""]

    args = compiler + sources_args + target_args + misc_args + optimization_args + include_args + link_args
    #print(" ".join(args))

    if activate_environment is None:
        ret = sp.run(args, check=False)
    else:
        ret = sp.run(activate_environment + args, shell=True, executable=shutil.which("powershell"), check=False)

    if ret.returncode != 0:
        coloprint(f"{Style.BRIGHT}{Fore.RED}Compilation failed with code {ret.returncode}.")
        sys.exit(ret.returncode)


def run(files, debug, output, terminal, binary, pause):
    """Run a binary, optionally compiling it from sources first."""
    if binary:
        exe = files[0]
    else:
        if not terminal:
            # Print helpful messages to separate building and running
            coloprint(f"{Style.BRIGHT}{Fore.CYAN}Building")

        build(files, debug, output)
        exe = output_name(files)

        if not terminal:
            # Print helpful messages to separate building and running
            coloprint(f"{Style.BRIGHT}{Fore.CYAN}Launching")

    if terminal:
        if sys.executable.endswith("kot.exe"):
            wrapper_executable = [sys.executable]
        else:
            wrapper_executable = [sys.executable, dir / "__main__.py"]

        sp.run(wrapper_executable + ["run", "-bp", exe], creationflags=sp.CREATE_NEW_CONSOLE, check=True)
    else:
        interactive_execute(exe, pause)

@atexit.register
def cleanup():
    shutil.rmtree(temp_dir)