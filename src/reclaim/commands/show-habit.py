"""Command to show a habit at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from datetime import date, timedelta

from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.exceptions import RecordNotFound
from rich.console import Console
from rich.table import Table

from ..completers import habit_ids
from ..str import str_duration, str_task_id
from ..utils import add_event_row
from .base import Command


class ShowHabitCommand(Command):
    """Show a habit at Reclaim.ai."""

    name = "show-habit"
    description = "show a habit"
    aliases = []

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)
        subparser.add_argument(
            "id", type=str, metavar="<id>", help="habit id to show"
        ).completer = habit_ids
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

        start = date.today()
        end = start + timedelta(days=90)
        events = client.get(
            "/api/events/v2",
            params={
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            },
        )
        occurrences = [
            e
            for e in events
            if (e.get("reclaimData") or {})
            .get("reclaimResourceId", {})
            .get("type")
            == "SmartSeriesId"
            and e.get("title") == habit["title"]
        ]
        occurrences.sort(
            key=lambda e: (e.get("eventDate") or {}).get("start", "")
        )
        has_more = len(occurrences) > 3
        occurrences = occurrences[:3]

        console = Console()
        console.print(f"Habit {hid}: {habit['title']}", style="bold underline")
        console.print(grid)
        if occurrences:
            habit_lookup = {habit["title"]: habit["id"]}
            occ_grid = Table(box=False, header_style="bold underline")
            occ_grid.add_column("Id")
            occ_grid.add_column("Date")
            occ_grid.add_column("Start")
            occ_grid.add_column("Dur", justify="right")
            occ_grid.add_column("Type", justify="center")
            occ_grid.add_column("Title")
            console.print()
            for e in occurrences:
                add_event_row(
                    e, occ_grid, multi_day=True, habit_lookup=habit_lookup
                )
            if has_more:
                occ_grid.add_row("...", "", "", "", "", "")
            console.print(occ_grid)
        return habit
