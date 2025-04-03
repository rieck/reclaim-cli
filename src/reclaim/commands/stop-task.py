"""Command to stop a task at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..utils import get_task, print_done
from .base import Command


class StopTaskCommand(Command):
    """Stop task at Reclaim.ai."""

    name = "stop-task"
    description = "stop a task"
    aliases = ["stop"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to stop"
        )

        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        # Add custom checks here
        return args

    def run(self, args):
        """Stop task at Reclaim.ai."""
        task = get_task(args.id)

        # Stop task
        task.stop()
        print_done("Stopped", task)
        return task
