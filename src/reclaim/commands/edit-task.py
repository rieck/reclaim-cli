"""Command to edit a task at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..utils import get_task, print_done
from .base import Command


class EditTaskCommand(Command):
    """Edit task at Reclaim.ai."""

    name = "edit-task"
    description = "edit a task"
    aliases = ["edit"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to start"
        )
        subparser.add_argument(
            "-t",
            "--title",
            type=str,
            metavar="<title>",
            help="title of the task",
            default=None,
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
        """Edit task at Reclaim.ai."""
        task = get_task(args.id)

        if args.title:
            task.title = args.title
        if args.due:
            task.due = args.due
        if args.snooze_until:
            task.snooze_until = args.snooze_until
        if args.priority:
            task.priority = args.priority
        if args.duration:
            task.duration = args.duration / 60  # Hours
        if args.min_chunk_size:
            task.min_chunk_size = int(args.min_chunk_size / 15)  # Chunks
        if args.max_chunk_size:
            task.max_chunk_size = int(args.max_chunk_size / 15)  # Chunks

        task.save()
        print_done("Edited", task)
        return task
