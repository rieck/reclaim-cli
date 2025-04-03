"""Command to show a task at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from rich.console import Console
from rich.table import Table

from ..utils import get_task, id_to_str, str_duration, str_task_status
from .base import Command


class ShowTaskCommand(Command):
    """Show a task at Reclaim.ai."""

    name = "show-task"
    description = "show a task"
    aliases = ["show"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to add time to"
        )

        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        # Add custom checks here
        return args

    def run(self, args):
        """Show task at Reclaim.ai."""
        task = get_task(args.id)
        tid = id_to_str(task.id)

        # Get status
        status = task.status.lower().replace("_", " ")
        state = str_task_status(task)
        time_required = task.time_chunks_required * 15
        time_spent = task.time_chunks_spent * 15
        progress = 1 if time_required == 0 else time_spent / time_required

        # Get chunk sizes
        min_time = str_duration(task.min_chunk_size * 15)
        max_time = str_duration(task.max_chunk_size * 15)

        def format_date(date):
            if date is None:
                return "N/A"
            return date.strftime("%Y-%m-%d %H:%M")

        grid = Table.grid(
            padding=(0, 3),
            pad_edge=True,
        )
        grid.add_row(
            "Status:",
            f"{state} ({status})",
            "Priority:",
            task.priority,
        )
        grid.add_row(
            "Time required:",
            str_duration(time_required),
            "Time spent:",
            str_duration(time_spent),
        )
        grid.add_row(
            "Chunk size:",
            f"{min_time} - {max_time}",
            "Progress:",
            f"{progress:.0%}",
        )
        grid.add_row(
            "Due date:",
            format_date(task.due),
            "Snooze:",
            format_date(task.snooze_until),
        )
        grid.add_row(
            "Created:",
            format_date(task.created),
            "Finished:",
            format_date(task.finished),
        )
        grid.add_row(
            "At risk:",
            "yes" if task.at_risk else "no",
            "On deck:",
            "yes" if task.on_deck else "no",
        )
        grid.add_row(
            "Adjusted:",
            "yes" if task.adjusted else "no",
            "Deferred:",
            "yes" if task.deferred else "no",
        )

        # Print table
        console = Console()
        console.print(f"Task {tid}: {task.title}", style="bold underline")
        console.print(grid)
        return task
