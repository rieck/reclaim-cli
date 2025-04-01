# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to delete a task at Reclaim.ai

from .base import Command
from ..utils import get_task, str_to_id, print_done


class DeleteTaskCommand(Command):
    """Delete a task at Reclaim.ai"""

    name = "delete-task"
    description = "delete a task"
    aliases = ["delete"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "ids", type=str, metavar="<id>", nargs="+",
            help="task id to delete"
        )

        return subparser

    def run(self, args):
        """Delete tasks at Reclaim.ai"""
        for task_id in args.ids:
            task = get_task(task_id)

            # Delete task
            task.delete()
            print_done(f"Deleted", task)
        return None
