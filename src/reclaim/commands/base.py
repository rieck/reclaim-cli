# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Base class for CLI commands

from ..utils import HelpFormatter


class Command(object):
    """Abstract base class for CLI commands."""

    name = None         # Command name
    description = None  # Command description
    aliases = []        # Command aliases

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = subparsers.add_parser(
            self.name, help=self.description, aliases=self.aliases,
            formatter_class=HelpFormatter
        )
        subparser.set_defaults(func=self.run)
        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        pass

    def run(self, args):
        """Execute the command."""
        pass
