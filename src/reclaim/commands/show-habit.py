"""Command to show a habit at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.exceptions import RecordNotFound
from rich.console import Console
from rich.table import Table

from ..str import str_duration, str_task_id
from .base import Command


class ShowHabitCommand(Command):
    """Show a habit at Reclaim.ai."""

    name = "show-habit"
    description = "show a habit"
    aliases = ["habit"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)
        subparser.add_argument(
            "id", type=str, metavar="<id>", help="habit id to show"
        )
        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)
        return args

    def run(self, args):
        """Show habit at Reclaim.ai."""
        client = ReclaimClient()
        try:
            habit = client.get(f"/api/assist/habits/daily/{args.id}")
        except RecordNotFound:
            raise ValueError(f"Habit not found: {args.id}")

        hid = "h" + str_task_id(habit["id"])[1:]

        def fmt(val):
            if val is None:
                return "N/A"
            return str(val)

        duration_min = str_duration(habit.get("durationMin") or 0)
        duration_max = str_duration(habit.get("durationMax") or 0)
        ideal_time = (habit.get("idealTime") or "")[:5] or "N/A"
        active = "enabled" if habit.get("elevated") else "disabled"
        private = "yes" if habit.get("alwaysPrivate") else "no"
        category = (habit.get("eventCategory") or "N/A").lower()
        defense = (habit.get("defenseAggression") or "N/A").lower()
        recurrence = habit.get("recurringAssignmentType") or ""
        recurrence = recurrence.replace("_HABIT", "").lower() or "N/A"
        priority = habit.get("priority") or "N/A"

        def fmt_date(val):
            return val[:10] if val else "N/A"

        grid = Table.grid(padding=(0, 3), pad_edge=True)
        grid.add_row("Status:", active, "Priority:", priority)
        grid.add_row(
            "Duration:",
            f"{duration_min} - {duration_max}",
            "Ideal time:",
            ideal_time,
        )
        grid.add_row("Recurrence:", recurrence, "Category:", category)
        grid.add_row(
            "Created:", fmt_date(habit.get("created")), "Defense:", defense
        )
        grid.add_row(
            "Updated:", fmt_date(habit.get("updated")), "Private:", private
        )

        console = Console()
        console.print(f"Habit {hid}: {habit['title']}", style="bold underline")
        console.print(grid)
        return habit
