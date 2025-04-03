"""Command to delete a task at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..utils import get_task, print_done
from .base import Command


class DeleteTaskCommand(Command):
    """Delete a task at Reclaim.ai."""

    name = "delete-task"
    description = "delete a task"
    aliases = ["delete"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to delete"
        )

        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        # Add custom checks here
        return args

    def run(self, args):
        """Delete tasks at Reclaim.ai."""
        task = get_task(args.id)

        # Delete task
        task.delete()
        print_done("Deleted", task)
        return None
