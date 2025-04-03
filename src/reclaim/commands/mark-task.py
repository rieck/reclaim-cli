"""Command to mark a task as complete or incomplete at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..utils import get_task, print_done
from .base import Command


class MarkTaskCommand(Command):
    """Mark a task at Reclaim.ai."""

    name = "mark-task"
    description = "mark a task (in)complete"
    aliases = ["mark"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to add time to"
        )
        subparser.add_argument(
            "mark",
            type=str,
            metavar="<mark>",
            default="complete",
            help="mark to set: complete, incomplete",
        )

        return subparser

    def validate_args(self, args):
        """Check and convert command line arguments."""
        super().validate_args(args)

        available_marks = ["complete", "incomplete"]
        if args.mark not in available_marks:
            raise ValueError(f"Invalid mark: Must be {available_marks}")

        return args

    def run(self, args):
        """Mark task at Reclaim.ai."""
        task = get_task(args.id)

        # Mark task
        if args.mark == "complete":
            task.mark_complete()
        else:
            task.mark_incomplete()

        print_done(f"Marked: {args.mark}", task)
        return task
