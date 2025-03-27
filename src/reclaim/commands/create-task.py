# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to create a task at Reclaim.ai

from reclaim_sdk.resources.task import Task, TaskPriority
from .base import Command
from ..utils import print_done, parse_duration
import dateparser


class CreateTaskCommand(Command):
    """Create a task at Reclaim.ai"""

    name = "create-task"
    description = "create a task"
    aliases = ["create"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "title", type=str, metavar="<title>",
            help="title of the task"
        )

        subparser.add_argument(
            "-d", "--due", type=str, metavar="<datetime>",
            help="due date of the task", default=None
        )
        subparser.add_argument(
            "-p", "--priority", type=str, metavar="<priority>",
            help="priority of the task", default=None
        )
        subparser.add_argument(
            "-D", "--duration", type=str, metavar="<duration>",
            help="duration of the task", default=None
        )
        subparser.add_argument(
            "-m", "--min-chunk-size", type=str, metavar="<duration>",
            help="minimum chunk size of the task", default=None
        )
        subparser.add_argument(
            "-M", "--max-chunk-size", type=str, metavar="<duration>",
            help="maximum chunk size of the task", default=None
        )

        return subparser

    def validate_args(self, args):
        """Check and convert command line arguments."""
        if args.due:
            try:
                args.due = dateparser.parse(args.due)
            except ValueError as e:
                raise ValueError(f"Invalid due date: {str(e)}")

        if args.priority:
            priority_num = args.priority.lower().lstrip('p')
            if priority_num not in ['1', '2', '3', '4']:
                raise ValueError("Priority must be between 1-4")
            args.priority = getattr(TaskPriority, f'P{priority_num}')

        return args

    def run(self, args):
        """Create task at Reclaim.ai"""
        task_args = {'title': args.title}

        # Prepare optional arguments
        if args.due:
            task_args['due'] = args.due
        if args.priority:
            task_args['priority'] = args.priority

        # Create task and save it
        task = Task(**task_args)

        # Set optional arguments
        if args.duration:
            task.duration = parse_duration(args.duration) / 60
        if args.min_chunk_size:
            task.min_chunk_size = parse_duration(args.min_chunk_size) / 60
        if args.max_chunk_size:
            task.max_chunk_size = parse_duration(args.max_chunk_size) / 60

        # Save task
        task.save()
        print_done(f"Created", task)
