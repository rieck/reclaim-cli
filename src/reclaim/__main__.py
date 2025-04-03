"""Reclaim CLI Main.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import argparse
import os
import sys

import reclaim.commands as commands
from reclaim.utils import HelpFormatter, load_config, set_api_key


def parse_args(cmds):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="reclaim",
        description="Reclaim CLI",
        formatter_class=HelpFormatter,
    )

    # Global options
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="<file>",
        default="~/.reclaim",
        help="set config file",
    )

    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", required=True)
    for cmd in cmds:
        cmd.parse_args(subparsers)

    # Parse global args
    args = parser.parse_args()

    # Expand user home directory
    args.config = os.path.expanduser(args.config)

    # Validate arguments
    for cmd in cmds:
        if args.command == cmd.name or args.command in cmd.aliases:
            cmd.validate_args(args)

    return args


def format_exception(error):
    """Format an error message."""
    return f"Error: {str(error)}"


def main():
    """Run the Reclaim CLI."""
    try:
        cmds = commands.load()
        args = parse_args(cmds)
        args = load_config(args)
        set_api_key(args)
        args.func(args)

    except Exception as e:
        print(format_exception(e), file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
