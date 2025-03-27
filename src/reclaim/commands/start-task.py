# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to start a task (or put it up-next) at Reclaim.ai

from .base import Command
from ..utils import get_task, str_to_id, print_done


class StartTaskCommand(Command):
    """Start task at Reclaim.ai"""

    name = "start-task"
    description = "start a task"
    aliases = ["start"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>",
            help="task id to start"
        )

        subparser.add_argument(
            "-n", "--up-next", action="store_true",
            help="start task in next available slot"
        )

        return subparser

    def validate_args(self, args):
        """Check and convert command line arguments."""
        try:
            args.id = str_to_id(args.id)
        except ValueError as e:
            raise ValueError(f"Invalid task ID: {str(e)}")
        return args

    def run(self, args):
        """Start task at Reclaim.ai"""
        task = get_task(args.id)

        if args.up_next:
            # Start task in next available slot
            task.up_next = True
            task.save()
            print_done(f"Up next", task)
        else:
            # Start task immediately
            task.start()
            print_done(f"Started", task)
