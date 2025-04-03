"""Command to create a task at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from reclaim_sdk.resources.task import Task

from ..utils import print_done
from .base import Command


class CreateTaskCommand(Command):
    """Create a task at Reclaim.ai."""

    name = "create-task"
    description = "create a task"
    aliases = ["create"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "title", type=str, metavar="<title>", help="title of the task"
        )

        subparser.add_argument(
            "-d",
            "--due",
            type=str,
            metavar="<datetime>",
            help="due date of the task",
            default=None,
        )
        subparser.add_argument(
            "-p",
            "--priority",
            type=str,
            metavar="<priority>",
            help="priority of the task",
            default=None,
        )
        subparser.add_argument(
            "-D",
            "--duration",
            type=str,
            metavar="<duration>",
            help="duration of the task",
            default=None,
        )
        subparser.add_argument(
            "-m",
            "--min-chunk-size",
            type=str,
            metavar="<duration>",
            help="minimum chunk size",
            default=None,
        )
        subparser.add_argument(
            "-M",
            "--max-chunk-size",
            type=str,
            metavar="<duration>",
            help="maximum chunk size",
            default=None,
        )
        subparser.add_argument(
            "-s",
            "--snooze-until",
            type=str,
            metavar="<datetime>",
            help="snooze until",
            default=None,
        )

        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        # Add custom checks here
        return args

    def run(self, args):
        """Create task at Reclaim.ai."""
        task_args = {"title": args.title}

        # Prepare optional arguments
        if args.due:
            task_args["due"] = args.due
        if args.snooze_until:
            task_args["snoozeUntil"] = args.snooze_until
        if args.priority:
            task_args["priority"] = args.priority

        # Create task and save it
        task = Task(**task_args)

        # Set optional arguments
        if args.duration:
            task.duration = args.duration / 60  # Hours
        if args.min_chunk_size:
            task.min_chunk_size = int(args.min_chunk_size / 15)  # Chunks
        if args.max_chunk_size:
            task.max_chunk_size = int(args.max_chunk_size / 15)  # Chunks

        # Save task
        task.save()
        print_done("Created", task)
        return task
