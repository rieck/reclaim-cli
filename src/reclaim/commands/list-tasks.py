# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to list tasks at Reclaim.ai

from rich.table import Table
from rich.console import Console
from reclaim_sdk.resources.task import Task, TaskStatus
from .base import Command
from ..utils import str_to_list, str_to_id, id_to_str, str_duration, str_task_status
import dateparser


class ListTasksCommand(Command):
    """List tasks at Reclaim.ai"""

    name = "list-tasks"
    description = "list tasks"
    aliases = ["list"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "-s", "--status", type=str, metavar="<list>",
            help="filter by status", default="active"
        )
        subparser.add_argument(
            "-i", "--id", type=str, metavar="<list>",
            help="filter by task IDs", default="all"
        )
        subparser.add_argument(
            "-d", "--due", type=str, metavar="<datetime>",
            help="filter by due date", default="all"
        )
        subparser.add_argument(
            "-r", "--at-risk", action="store_true",
            help="show only at-risk tasks"
        )
        subparser.add_argument(
            "-o", "--order", type=str, metavar="<field>",
            help="order by field", default="due"
        )

    def validate_args(self, args):
        """Check and convert command line arguments."""
        # Custom state: active -> new,scheduled,in_progress
        if args.status == "active":
            args.status = "new,scheduled,in_progress"

        # Convert status strings to enums
        try:
            status_list = str_to_list(args.status)
            args.status = [] if "all" in status_list else [
                TaskStatus[s.upper()] for s in status_list
            ]
        except KeyError as e:
            raise ValueError(f"Invalid task status: {str(e)}")

        # Convert ID strings to integers
        try:
            id_list = str_to_list(args.id)
            args.id = [] if "all" in id_list else [
                str_to_id(id_str) for id_str in id_list
            ]
        except ValueError as e:
            raise ValueError(f"Invalid task ID: {str(e)}")

        # Parse due date
        try:
            args.due = None if args.due == "all" else dateparser.parse(
                args.due)
        except ValueError as e:
            raise ValueError(f"Invalid due date: {str(e)}")

        return args

    def run(self, args):
        """List (filtered and sorted) tasks."""
        tasks = self.sort_tasks(Task.list(), args)

        grid = Table(box=False)

        grid.add_column("Id")
        grid.add_column("Due")
        grid.add_column("Left", justify="right")
        grid.add_column("Prog", justify="right")
        grid.add_column("State", justify="center")
        grid.add_column("Title", justify="left")

        # Print tasks
        for task in tasks:
            if self.filter_task(task, args):
                self.add_task(task, grid)

        console = Console()
        console.print(grid)

    def add_task(self, task, grid):
        """Format and add a task to the grid."""
        short_id = id_to_str(task.id)
        due_date = task.due.strftime("%Y-%m-%d") if task.due else "anytime"

        # Calculate progress metrics
        if task.time_chunks_required == 0:
            left, progress = 0, 1
        else:
            left = task.time_chunks_remaining
            progress = task.time_chunks_spent / task.time_chunks_required

        left = str_duration(left * 15)
        status = str_task_status(task)

        grid.add_row(
            short_id, due_date, left, f"{progress:.0%}", status, task.title
        )

    def filter_task(self, task, args):
        """Check if task matches filter criteria."""
        if args.status and task.status not in args.status:
            return False
        if args.id and task.id not in args.id:
            return False
        if args.at_risk and not task.at_risk:
            return False
        if (args.due and task.due and
                task.due >= args.due.replace(tzinfo=task.due.tzinfo)):
            return False
        return True

    def sort_tasks(self, tasks, args):
        """Sort tasks by specified field."""

        sort_keys = {
            "id": lambda x: x.id,
            "due": lambda x: (1, None) if not x.due else (0, x.due),
            "left": lambda x: -x.time_chunks_remaining,
            "progress": lambda x: -x.time_chunks_remaining / (x.time_chunks_required + 1),
            "prog": lambda x: -x.time_chunks_remaining / (x.time_chunks_required + 1),
            "status": lambda x: x.status,
            "state": lambda x: x.status,
            "title": lambda x: x.title
        }

        try:
            return sorted(tasks, key=sort_keys[args.order])
        except KeyError:
            raise ValueError(f"Invalid order field: {args.order}")
