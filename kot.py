import sys
import os
import atexit
import shutil
import subprocess
from pathlib import Path
from argparse import ArgumentParser

def resolved(path):
    """Resolve a path, eliminating symlinks and special characters like `.`, `..`, `~`."""
    return Path(path).expanduser().resolve()

is_frozen = sys.executable.endswith("kot.exe")

dir = Path(__file__).parent

temp_dir = resolved(f"~/AppData/Local/Temp/kot/{os.getpid()}")
Path(temp_dir).mkdir(parents=True, exist_ok=True)

include_dir = resolved("~/vcpkg/installed/x64-windows-static/include")
lib_dir = resolved("~/vcpkg/installed/x64-windows-static/lib")

if is_frozen:
    vswhere_path = dir / "vswhere.exe"
else:
    vswhere_path = dir / "data/vswhere.exe"


def output_name(sources, override=None):
    """Calculate output path. Usually it's sources[0] with an `.exe` suffix. If override is not None, use override."""
    if override is not None:
        result = resolved(override)
        if result.suffix != ".exe":
            result += ".exe"
        return result

    return resolved(sources[0]).with_suffix(".exe")


def interactive_execute(exe, pause=False):
    """Execute something. Pring exit code and optionally pause for user input in the end."""
    ret = subprocess.run(exe)

    if pause:
        print(f"\nProcess exited with code {ret.returncode}", end="")
        input()
    else:
        print(f"\nProcess exited with code {ret.returncode}")


def build(sources, debug, output):
    """Build an executable from a list of sources. Currently only cl.exe is supported."""
    # Determine compiler
    cl_location = shutil.which("cl")
    if cl_location is None:
        ret = subprocess.run([vswhere_path, "-property", "InstallationPath"], text=True, capture_output=True)
        
        if ret.stdout == "":
            print("Could not find Visual Studio.")
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
    sources_args = [str(Path(source).expanduser().resolve()) for source in sources]
    target_args = ["/Fe:", output_name(sources, output)]
    misc_args = ["/std:c++latest", "/W3", "/nologo", "/EHsc", "/Zc:preprocessor", "/Fo:", str(temp_dir) + "\\"]
    optimization_args = [
        "/Od" if debug else "/O2",
        "/MTd" if debug else "/MT"
    ]
    include_args = ["/I", str(include_dir)]
    link_args = ["/link", f"/LIBPATH:\"{lib_dir}\""]

    args = compiler + sources_args + target_args + misc_args + optimization_args + include_args + link_args

    if activate_environment is None:
        ret = subprocess.run(args)
    else:
        ret = subprocess.run(activate_environment + args, shell=True, executable=shutil.which("powershell"))

    if ret.returncode != 0:
        print(f"Compilation failed with code {ret.returncode}.")
        sys.exit(ret.returncode)


def run(files, debug, output, terminal, binary, pause):
    """Run a binary, optionally compiling it from sources first."""
    if binary:
        exe = files[0]
    else:
        build(files, debug, output)
        exe = output_name(files)
    
    if terminal:
        if is_frozen:
            wrapper_executable = [sys.executable]
        else:
            wrapper_executable = ["python", __file__]

        subprocess.run(wrapper_executable + ["run", "-bp", exe], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        interactive_execute(exe, pause)


def main():
    parser = ArgumentParser("kot")
    parser.set_defaults(subcommand="none")
    subparsers = parser.add_subparsers(title="subcommands")

    parser_build = subparsers.add_parser("build")
    parser_build.set_defaults(subcommand="build")
    parser_build.add_argument("sources", nargs="+")
    parser_build.add_argument("-d", "--debug", action="store_true")
    parser_build.add_argument("-o", "--output")

    parser_run = subparsers.add_parser("run")
    parser_run.set_defaults(subcommand="run")
    parser_run.add_argument("files", nargs="+")
    parser_run.add_argument("-b", "--binary", action="store_true")
    parser_run.add_argument("-d", "--debug", action="store_true")
    parser_run.add_argument("-o", "--output")
    decorations = parser_run.add_mutually_exclusive_group()
    decorations.add_argument("-p", "--pause", action="store_true")
    decorations.add_argument("-t", "--terminal", action="store_true")

    args = parser.parse_args()
    if args.subcommand == "build":
        build(args.sources, args.debug, args.output)
    elif args.subcommand == "run":
        if args.binary and len(args.files) != 1:
            parser_run.print_usage()
            print("kot run: error: argument -b/--binary: not allowed with multiple files specified")
            return 1
        
        if args.binary and args.output:
            parser_run.print_usage()
            print("kot run: error: argument -b/--binary: not allowed with with argument -o/--output")
            return 1
        
        if args.binary and args.debug:
            parser_run.print_usage()
            print("kot run: error: argument -b/--binary: not allowed with with argument -d/--debug")
            return 1

        run(args.files, args.debug, args.output, args.terminal, args.binary, args.pause)


@atexit.register
def cleanup():
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    sys.exit(main())
