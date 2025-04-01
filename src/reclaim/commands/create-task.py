# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to create a task at Reclaim.ai

from reclaim_sdk.resources.task import Task, TaskPriority
from .base import Command
from ..utils import print_done, parse_duration, parse_datetime


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
            help="minimum chunk size", default=None
        )
        subparser.add_argument(
            "-M", "--max-chunk-size", type=str, metavar="<duration>",
            help="maximum chunk size", default=None
        )
        subparser.add_argument(
            "-s", "--snooze-until", type=str, metavar="<datetime>",
            help="snooze until", default=None
        )

        return subparser

    def validate_args(self, args):
        """Check and convert command line arguments."""
        if args.due:
            try:
                args.due = parse_datetime(args.due)
            except ValueError as e:
                raise ValueError(f"Invalid due date: {str(e)}")
        if args.snooze_until:
            try:
                args.snooze_until = parse_datetime(args.snooze_until)
            except ValueError as e:
                raise ValueError(f"Invalid snooze date: {str(e)}")
        if args.priority:
            priority_num = args.priority.lower().lstrip('p')
            if priority_num not in ['1', '2', '3', '4']:
                raise ValueError("Priority must be between 1-4")
            args.priority = getattr(TaskPriority, f'P{priority_num}')
        if args.duration:
            try:
                args.duration = parse_duration(args.duration)
            except ValueError as e:
                raise ValueError(f"Invalid duration: {str(e)}")
        if args.min_chunk_size:
            try:
                args.min_chunk_size = parse_duration(args.min_chunk_size)
            except ValueError as e:
                raise ValueError(f"Invalid minimum chunk size: {str(e)}")
        if args.max_chunk_size:
            try:
                args.max_chunk_size = parse_duration(args.max_chunk_size)
            except ValueError as e:
                raise ValueError(f"Invalid maximum chunk size: {str(e)}")

        return args

    def run(self, args):
        """Create task at Reclaim.ai"""
        task_args = {'title': args.title}

        # Prepare optional arguments
        if args.due:
            task_args['due'] = args.due
        if args.snooze_until:
            task_args['snoozeUntil'] = args.snooze_until
        if args.priority:
            task_args['priority'] = args.priority

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
        print_done(f"Created", task)
        return task