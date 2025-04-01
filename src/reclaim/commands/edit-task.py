# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to edit a task at Reclaim.ai

from reclaim_sdk.resources.task import TaskPriority
from .base import Command
from ..utils import get_task, str_to_id, print_done, parse_duration, parse_datetime


class EditTaskCommand(Command):
    """Edit task at Reclaim.ai"""

    name = "edit-task"
    description = "edit a task"
    aliases = ["edit"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>",
            help="task id to start"
        )

        subparser.add_argument(
            "-t", "--title", type=str, metavar="<title>",
            help="title of the task", default=None
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
        try:
            args.id = str_to_id(args.id)
        except ValueError as e:
            raise ValueError(f"Invalid task ID: {str(e)}")

        if args.snooze_until:
            try:
                args.snooze_until = parse_datetime(args.snooze_until)
            except ValueError as e:
                raise ValueError(f"Invalid snooze date: {str(e)}")

        if args.due:
            try:
                args.due = parse_datetime(args.due)
            except ValueError as e:
                raise ValueError(f"Invalid due date: {str(e)}")

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
        """Start task at Reclaim.ai"""
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
        print_done(f"Edited", task)
        return task