"""Command to start a task (or put it up-next) at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..utils import get_task, print_done
from .base import Command


class StartTaskCommand(Command):
    """Start task at Reclaim.ai."""

    name = "start-task"
    description = "start a task"
    aliases = ["start"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to start"
        )

        subparser.add_argument(
            "-n",
            "--up-next",
            action="store_true",
            help="start task in next available slot",
        )

        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        # Add custom checks here
        return args

    def run(self, args):
        """Start task at Reclaim.ai."""
        task = get_task(args.id)

        if args.up_next:
            # Start task in next available slot
            task.up_next = True
            task.save()
            print_done("Up next", task)
        else:
            # Start task immediately
            task.start()
            print_done("Started", task)
        return task
