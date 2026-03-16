"""Command to show configuration template for Reclaim CLI.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from collections import defaultdict
from datetime import date, timedelta

from reclaim_sdk.client import ReclaimClient

from ..str import _EVENT_COLORS
from .base import Command

_COLOR_NAMES = ", ".join(c.lower() for c in _EVENT_COLORS)


class ConfigCommand(Command):
    """Show configuration template for Reclaim CLI."""

    name = "config"
    description = "show config template"
    aliases = []

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        return super().parse_args(subparsers)

    def run(self, args):
        """Print a configuration template with discovered calendar IDs."""
        client = ReclaimClient()
        start = date.today()
        end = start + timedelta(days=60)
        events = client.get(
            "/api/events/v2",
            params={
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
                "allConnected": "true",
            },
        )

        by_cal = defaultdict(list)
        for e in events:
            rd = e.get("reclaimData") or {}
            if rd.get("reclaimEventType") == "USER":
                cal_id = e.get("calendarId")
                if cal_id:
                    by_cal[cal_id].append(e.get("title", ""))

        print("# Reclaim CLI configuration (~/.reclaim)\n")
        print("reclaim_token: <token>\n")

        if not by_cal:
            return

        print("# Available calendars:")
        print("calendars:")
        for cal_id, titles in sorted(by_cal.items()):
            print(f"  {cal_id}:  # Next event: {titles[0]}")
            print("    name:")
            print("    color: sage")
        print(f"\n# Available colors: {_COLOR_NAMES}")
