import os
import subprocess as sp
import sys
from pathlib import Path

from kot.__main__ import main
from kot.cli import cli

from atleave import atleave

thisdir = Path(__file__).parent
os.chdir(thisdir)


def delete_exe():
    for path in thisdir.rglob("*.exe"):
        path.unlink()


def run(*args):
    _argv = sys.argv

    def reset_argv():
        sys.argv = _argv

    with atleave(reset_argv):
        # CliRunner does not expand globs for some reason
        sys.argv = ["kot"] + list(args)
        return main()


def test_help(capsys):
    ret = run("--help")
    assert ret == 0

    stdout, stderr = capsys.readouterr()
    for subcommand in cli.commands.keys():
        assert subcommand in stdout


def test_help_subcommands(capsys):
    def perform_test(command):
        ret = run(command, "--help")
        assert ret == 0

        stdout, stderr = capsys.readouterr()
        assert command in stdout

    for subcommand in cli.commands.keys():
        perform_test(subcommand)


def test_build():
    with atleave(delete_exe):
        ret = run("build", "proj_manyfiles/main.cpp", "proj_manyfiles/print.cpp")

        assert ret == 0
        assert Path("app.exe").is_file()


def test_build_output():
    with atleave(delete_exe):
        ret = run("build", "proj_manyfiles/main.cpp", "proj_manyfiles/print.cpp", "--output", "abc.exe")

        assert ret == 0
        assert Path("abc.exe").is_file()


def test_build_glob():
    with atleave(delete_exe):
        ret = run("build", "proj_manyfiles/*.cpp")

        assert ret == 0
        assert Path("app.exe").is_file()


def test_build_debug():
    def perform_test(output, args):
        with atleave(delete_exe):
            ret = run(*args)

            assert ret == 0
            assert Path("main.exe").is_file()

            exec_result = sp.run(["main.exe"], capture_output=True, check=False)
            assert exec_result.returncode == 0
            assert exec_result.stdout == output

    perform_test(b"debug", ["build", "proj_debug/main.cpp", "--debug"])
    perform_test(b"release", ["build", "proj_debug/main.cpp", "--release"])
    perform_test(b"release", ["build", "proj_debug/main.cpp"])


def test_launch():
    ret = run("build", "proj_manyfiles/*.cpp", "--output", "test_launch.exe")
    assert ret == 0
    assert Path("test_launch.exe").is_file()

    ret = run("launch", "test_launch.exe")
    assert ret == 0
