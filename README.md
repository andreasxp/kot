# Kot
A very simple to use code builder for C++, packed with usability features for compiling single files and small projects.
Kot is an entirely CLI tool, no graphical interface.

## Installation
Kot requires Python 3 and pip. Download the latest release via pip like so:
```
pip install https://github.com/andreasxp/kot/archive/refs/tags/0.3.1.zip
```
Kot will notify you when a new version is available.

## Usage
Since Kot is a CLI tool, consult the very helpful `--help` command for more information on what Kot can do. Here's a sample:
```
$ kot --help
Usage: kot [OPTIONS] COMMAND [ARGS]...

  A very simple C++ builder and runner.

Options:
  -v         Enable verbose output.
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  build   Build a binary from C++ source files.
  config  View config entry 'name' or replace it with 'value', if specified.
  launch  Execute any command and print exit code.
  pg      Open an interactive C++ playground.
  run     Build and run a binary from C++ source files.
```
```
$ kot run --help
Usage: kot run [OPTIONS] SOURCES...

  Build and run a binary from C++ source files.

Options:
  -o, --output FILE            Output filename.  [default: (source name or 'app' for many sources)]
  -d, --debug / -r, --release  Building mode.  [default: release]
  -p, --pause                  Pause after execution.
  -t, --terminal               Open a separate terminal for output and pause after execution.
  --args TEXT                  Additional cli arguments for the executable.
  --help                       Show this message and exit.
```
