"""Command to add time to a task at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..utils import get_task, print_done, str_duration
from .base import Command


class AddTimeCommand(Command):
    """Add time to task at Reclaim.ai."""

    name = "add-time"
    description = "add time to a task"
    aliases = ["add"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to add time to"
        )
        subparser.add_argument(
            "duration", type=str, metavar="<duration>", help="duration to add"
        )

        return subparser

    def run(self, args):
        """Add time to task at Reclaim.ai."""
        task = get_task(args.id)

        # Add time to task
        task.add_time(args.duration / 60)  # Expects hours
        dur = str_duration(args.duration)
        print_done(f"Added: {dur}", task)

        return task
