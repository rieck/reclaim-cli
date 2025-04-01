# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Base class for CLI commands

from ..utils import HelpFormatter, str_to_id, str_to_ids, parse_datetime, parse_duration, parse_priority


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

    def run(self, args):
        """Execute the command."""
        pass

    def validate_args(self, args):
        """ Validate and transform command arguments. """
        check_args = {
            "id": str_to_id,
            "ids": str_to_ids,
            "snooze_until": parse_datetime,
            "due": parse_datetime,
            "log_time": parse_datetime,
            "priority": parse_priority,
            "duration": parse_duration,
            "min_chunk_size": parse_duration,
            "max_chunk_size": parse_duration
        }
        
        for name, validate in check_args.items():
            if hasattr(args, name):
                try:
                    setattr(args, name, validate(getattr(args, name)))
                except ValueError as e:
                    raise ValueError(f"Invalid {name}: {str(e)}")

        return args
