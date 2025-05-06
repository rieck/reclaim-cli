"""Command to list tasks at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from reclaim_sdk.resources.task import Task, TaskStatus
from rich.console import Console
from rich.table import Table

from ..utils import id_to_str, str_duration, str_task_status, str_to_list
from .base import Command


class ListTasksCommand(Command):
    """List tasks at Reclaim.ai."""

    name = "list-tasks"
    description = "list tasks"
    aliases = ["list"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)
        subparser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="show all tasks",
        )
        subparser.add_argument(
            "-s",
            "--status",
            type=str,
            metavar="<list>",
            help="filter by status: new, scheduled, in_progress, archived",
            default="active",
        )
        subparser.add_argument(
            "-d",
            "--due",
            type=str,
            metavar="<datetime>",
            help="filter by due date",
        )
        subparser.add_argument(
            "-r",
            "--at-risk",
            action="store_true",
            help="show only at-risk tasks",
        )
        subparser.add_argument(
            "-o",
            "--order",
            type=str,
            metavar="<field>",
            help="order by field: id, due, left, prog, status, title",
            default="due",
        )
        return subparser

    def validate_args(self, args):
        """Validate arguments."""
        super().validate_args(args)

        if args.status == "active":
            args.status = "new,scheduled,in_progress"

        if args.all:
            args.status = "all"

        # Convert status strings to enums
        try:
            status_list = str_to_list(args.status)
            args.status = (
                []
                if "all" in status_list
                else [TaskStatus[s.upper()] for s in status_list]
            )
        except KeyError as e:
            raise ValueError(f"Invalid task status: {str(e)}")

        return args

    def run(self, args):
        """List (filtered and sorted) tasks."""
        tasks = self.sort_tasks(Task.list(), args)

        grid = Table(box=False, header_style="bold underline")

        grid.add_column("Id")
        grid.add_column("Due")
        grid.add_column("Left", justify="right")
        grid.add_column("Prog", justify="right")
        grid.add_column("State", justify="center")
        grid.add_column("Title", justify="left")

        # Print tasks
        output = []
        for task in tasks:
            if self.filter_task(task, args):
                output.append(task)
                self.add_task(task, grid)

        console = Console()
        console.print(grid)
        return output

    def add_task(self, task, grid):
        """Format and add a task to the grid."""
        short_id = id_to_str(task.id)
        due_date = task.due.strftime("%Y-%m-%d") if task.due else "anytime"
        time_required = task.time_chunks_required * 15
        time_spent = task.time_chunks_spent * 15
        progress = 1 if time_required == 0 else time_spent / time_required
        status = str_task_status(task)

        grid.add_row(
            short_id,
            due_date,
            str_duration(time_required - time_spent),
            f"{progress:.0%}",
            status,
            task.title,
        )

    def filter_task(self, task, args):
        """Check if task matches filter criteria."""
        if args.status and task.status not in args.status:
            return False
        if args.at_risk and not task.at_risk:
            return False
        if (
            args.due
            and task.due
            and task.due >= args.due.replace(tzinfo=task.due.tzinfo)
        ):
            return False
        return True

    def sort_tasks(self, tasks, args):
        """Sort tasks by specified field."""

        def calculate_progress(task):
            """Calculate task progress score (negative for sorting)."""
            return -task.time_chunks_remaining / (
                task.time_chunks_required + 1
            )

        sort_keys = {
            "id": lambda x: x.id,
            "due": lambda x: (1, None) if not x.due else (0, x.due),
            "left": lambda x: -x.time_chunks_remaining,
            "progress": calculate_progress,
            "prog": calculate_progress,
            "status": lambda x: x.status,
            "state": lambda x: x.status,
            "title": lambda x: x.title,
        }

        try:
            return sorted(tasks, key=sort_keys[args.order])
        except KeyError:
            raise ValueError(f"Invalid order field: {args.order}")
