# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to stop a task at Reclaim.ai

from .base import Command
from ..utils import get_task, str_to_id, print_done


class StopTaskCommand(Command):
    """Stop task at Reclaim.ai"""

    name = "stop-task"
    description = "stop a task"
    aliases = ["stop"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>",
            help="task id to stop"
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
        """Stop task at Reclaim.ai"""
        task = get_task(args.id)
        
        # Stop task
        task.stop()
        print_done(f"Stopped", task)
