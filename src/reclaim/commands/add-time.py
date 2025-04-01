# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to create a task at Reclaim.ai

from ..utils import get_task, parse_duration, print_done, str_duration, str_to_id
from .base import Command


class AddTimeCommand(Command):
    """Add time to task at Reclaim.ai"""

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
        """Add time to task at Reclaim.ai"""
        task = get_task(args.id)

        # Add time to task
        mins = parse_duration(args.duration)
        task.add_time(mins / 60)  # Expects hours
        dur = str_duration(mins)
        print_done(f"Added: {dur}", task)
