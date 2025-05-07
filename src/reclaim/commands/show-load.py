"""Command to show workload at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from datetime import datetime, timedelta, timezone

from reclaim_sdk.resources.task import Task
from rich.console import Console
from rich.table import Table

from .base import Command


class ShowLoadCommand(Command):
    """Show estimated workload at Reclaim.ai."""

    name = "show-load"
    description = "show estimated workload"
    aliases = ["load"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "-w",
            "--weeks",
            type=int,
            metavar="<number>",
            help="number of weeks to look ahead",
            default=4,
        )

        subparser.add_argument(
            "-t",
            "--work-time",
            type=str,
            metavar="<duration>",
            help="working time per week",
            default="40h",
        )
        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        # Add custom checks here
        return args

    def next_monday(self, today):
        """Get date of next monday."""
        days_until_monday = (7 - today.weekday()) % 7
        monday = today.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_until_monday)
        return monday

    def run(self, args):
        """Show workload at Reclaim.ai."""
        # Get all tasks
        tasks = Task.list()
        table = Table(box=False, header_style="bold underline")

        # Add columns
        table.add_column("Week", justify="left")
        table.add_column("Start", justify="left")
        table.add_column("End", justify="left")
        table.add_column("Hours", justify="right")
        table.add_column("Load", justify="right")
        table.add_column("Tasks", justify="right")

        today = datetime.now(timezone.utc)
        monday = self.next_monday(today)

        for week in range(args.weeks):
            week_start = monday + timedelta(days=7 * week)
            week_end = week_start + timedelta(days=7)

            load = in_week = active = 0
            for task in tasks:
                work_left = (
                    task.time_chunks_required - task.time_chunks_spent
                ) / 4
                if work_left <= 0:
                    continue
                active += 1

                start = task.snooze_until or today
                if task.due < week_start or start > week_end:
                    continue

                in_week += 1
                start = max(start, today)
                load += 7 * (work_left / (task.due - start).days)

            table.add_row(
                f"W{week_start.isocalendar()[1]}",
                week_start.strftime("%Y-%m-%d"),
                week_end.strftime("%Y-%m-%d"),
                f"{load:.1f}h",
                f"{60*load/args.work_time:.1%}",
                f"{in_week}/{active}",
            )

        # Print table
        console = Console()
        console.print(table)

        return tasks
