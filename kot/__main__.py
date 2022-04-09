import sys
from argparse import ArgumentParser

import kot


def main():
    parser = ArgumentParser("kot", description="A very simple C++ builder and runner.")
    parser.set_defaults(subcommand=None)
    parser.add_argument("-V", "--version", action='version', version=kot.__version__)
    subparsers = parser.add_subparsers(title="subcommands")

    parser_build = subparsers.add_parser("build", description="Build a C++ file.")
    parser_build.set_defaults(subcommand="build")
    parser_build.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
    parser_build.add_argument("sources", nargs="+", help="one or more .cpp files to build")
    parser_build.add_argument("-d", "--debug", action="store_true", help="build in debug mode")
    parser_build.add_argument("-o", "--output", help="specify a different name for the output file")

    parser_run = subparsers.add_parser("run", description="Run a C++ file, compiling it first.")
    parser_run.set_defaults(subcommand="run")
    parser_run.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
    parser_run.add_argument("files", nargs="+", help="one or more .cpp files to build or a single binary file to run")
    parser_run.add_argument("-b", "--binary", action="store_true", help="run the binary file without building")
    parser_run.add_argument("-d", "--debug", action="store_true", help="build in debug mode")
    parser_run.add_argument("-o", "--output", help="specify a different name for the output file")
    decorations = parser_run.add_mutually_exclusive_group()
    decorations.add_argument("-p", "--pause", action="store_true", help="pause after executing")
    decorations.add_argument("-t", "--terminal", action="store_true", help="run in a separate terminal and pause")

    args = parser.parse_args()
    if args.subcommand == "build":
        if args.verbose:
            kot.print_debug = True

        kot.build(args.sources, args.debug, args.output)
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

        if args.verbose:
            kot.print_debug = True

        kot.run(args.files, args.debug, args.output, args.terminal, args.binary, args.pause)
    else:
        parser.error("missing subcommand")

    kot.prompt_to_update()


if __name__ == "__main__":
    sys.exit(main())
