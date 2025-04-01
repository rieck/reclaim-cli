# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Command to log work to a task at Reclaim.ai

from ..utils import (
    get_task,
    parse_datetime,
    parse_duration,
    print_done,
    str_duration,
    str_to_id,
)
from .base import Command


class LogWorkCommand(Command):
    """Log work to task at Reclaim.ai"""

    name = "log-work"
    description = "log work to a task"
    aliases = ["log"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task id to log work for"
        )
        subparser.add_argument(
            "duration", type=str, metavar="<duration>", help="duration of work"
        )
        subparser.add_argument(
            "-l",
            "--log_time",
            type=str,
            metavar="<datetime>",
            help="set log time",
            default="now",
        )

        return subparser

    def run(self, args):
        """Log work at Reclaim.ai"""
        task = get_task(args.id)

        # Log work
        mins = parse_duration(args.duration)
        task.log_work(mins, end=args.log_time)  # Expects minutes
        dur = str_duration(mins)

        print_done(f"Logged: {dur}", task)
        return task
