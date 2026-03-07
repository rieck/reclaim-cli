"""Command to list events at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from datetime import date, timedelta

from reclaim_sdk.client import ReclaimClient
from rich.console import Console
from rich.table import Table

from ..parse import parse_datetime
from ..utils import add_event_row
from .base import Command


class ListEventsCommand(Command):
    """List events at Reclaim.ai."""

    name = "list-events"
    description = "list calendar events"
    aliases = []

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "-d",
            "--date",
            type=str,
            metavar="<date>",
            help="show events for a specific date (default: today)",
            default=None,
        )
        subparser.add_argument(
            "-f",
            "--future",
            type=int,
            metavar="<days>",
            help="show events up to x days from the starting date",
            default=None,
        )

        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args = super().validate_args(args)

        if args.date:
            try:
                args.date = parse_datetime(args.date).date()
            except ValueError as e:
                raise ValueError(f"Invalid date: {e}")

        if args.future is not None and args.future < 1:
            raise ValueError("--future must be at least 1")

        return args

    def run(self, args):
        """List events at Reclaim.ai."""
        start = args.date if args.date else date.today()

        if args.future is not None:
            end = start + timedelta(days=args.future + 1)
            multi_day = True
        else:
            end = start + timedelta(days=1)
            multi_day = False

        client = ReclaimClient()
        events = client.get(
            "/api/events/v2",
            params={
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            },
        )
        events.sort(key=lambda e: (e.get("eventDate") or {}).get("start", ""))

        habits = client.get("/api/assist/habits/daily")
        habit_lookup = {h["title"]: h["id"] for h in habits}

        grid = Table(box=False, header_style="bold underline")
        grid.add_column("Id")
        if multi_day:
            grid.add_column("Date")
        grid.add_column("Start")
        grid.add_column("Dur", justify="right")
        grid.add_column("Type", justify="center")
        grid.add_column("Title")

        for event in events:
            add_event_row(event, grid, multi_day, habit_lookup)

        Console().print(grid)
        return events
