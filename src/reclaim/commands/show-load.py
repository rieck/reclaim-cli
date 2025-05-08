"""Command to show workload at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from datetime import datetime, timedelta, timezone

from reclaim_sdk.resources.task import Task
from rich.console import Console
from rich.table import Table

from ..str import str_tid
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

    def task_load(self, task, today):
        """Calculate remaining workload for a task."""
        work_left = (task.time_chunks_required - task.time_chunks_spent) / 4
        if work_left <= 0:
            return 0

        start = max(task.snooze_until or today, today)
        days_left = (task.due - start).days
        return 7 * (work_left / days_left) if days_left > 0 else 0

    def format_task_list(self, tasks, cutoff=4):
        """Format list of task IDs."""
        if len(tasks) <= cutoff:
            return " ".join(str_tid(t.id) for t in tasks)
        return " ".join(str_tid(t.id) for t in tasks[: cutoff - 1]) + " ..."

    def create_load_table(self):
        """Create table for workload display."""
        table = Table(box=False, header_style="bold underline")
        columns = [
            ("Week", "left"),
            ("Start", "left"),
            ("End", "left"),
            ("Hours", "right"),
            ("Load", "right"),
            ("Num", "right"),
            ("Tasks", "left"),
        ]
        for name, justify in columns:
            table.add_column(name, justify=justify)
        return table

    def run(self, args):
        """Show workload at Reclaim.ai."""
        tasks = Task.list()
        table = self.create_load_table()
        today = datetime.now(timezone.utc)
        monday = self.next_monday(today)

        for week in range(args.weeks):
            week_start = monday + timedelta(days=7 * week)
            week_end = week_start + timedelta(days=7)

            # Get active tasks
            active_tasks = [t for t in tasks if self.task_load(t, today) > 0]

            # Filter tasks that are within the week
            week_tasks = []
            for t in active_tasks:
                too_early = t.due < week_start
                too_late = (t.snooze_until or today) > week_end
                if not (too_early or too_late):
                    week_tasks.append(t)

            # Calculate total load for the week
            total_load = sum(self.task_load(t, today) for t in week_tasks)

            table.add_row(
                f"W{week_start.isocalendar()[1]}",
                week_start.strftime("%Y-%m-%d"),
                week_end.strftime("%Y-%m-%d"),
                f"{total_load:.1f}h",
                f"{60*total_load/args.work_time:.1%}",
                f"{len(week_tasks)}",
                self.format_task_list(sorted(week_tasks, key=lambda t: t.due)),
            )

        Console().print(table)
        return tasks
