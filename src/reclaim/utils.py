"""Utility Functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import argparse
import os

import yaml
from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.exceptions import RecordNotFound
from reclaim_sdk.resources.task import Task

from .parse import parse_event_time
from .str import (
    scramble_id,
    str_duration,
    str_event_color,
    str_event_id,
    str_event_type,
    str_task_id,
    str_tid,
)


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Custom help formatter with fixed width and position."""

    def __init__(self, prog):
        """Initialize the help formatter."""
        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 80  # fallback if terminal size can't be determined
        super().__init__(prog, max_help_position=24, width=width)

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = "usage: "

        # Only modify main command usage, not subcommands
        if self._prog == "reclaim":  # Check if we're formatting main command
            # Find the subparser action
            subparser_action = None
            for action in actions:
                if isinstance(action, argparse._SubParsersAction):
                    subparser_action = action
                    break

            if subparser_action:
                # Use <command> instead of listing all commands
                return f"{prefix}{self._prog} [options] <command> ...\n\n"

        # For subcommands, use default usage formatting
        return super()._format_usage(usage, actions, groups, prefix)

    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            # Get the original format but remove the first line
            parts = super()._format_action(action).split("\n")
            return "\n".join(parts[1:])
        return super()._format_action(action)


def load_config(args):
    """Load configuration file."""
    args.config = os.path.expanduser(args.config)
    if not os.path.exists(args.config):
        return args

    with open(args.config) as f:
        config = yaml.safe_load(f)
        for key, value in config.items():
            setattr(args, key, value)

    return args


def set_api_key(cfg):
    """Set the API key in the configuration file."""
    token = None
    if os.environ.get("RECLAIM_TOKEN"):
        token = os.environ.get("RECLAIM_TOKEN")
    elif hasattr(cfg, "reclaim_token"):
        token = cfg.reclaim_token
    if not token:
        raise Exception("No Reclaim API token set")
    ReclaimClient.configure(token=token)


def get_task(task_id):
    """Get a task from Reclaim.ai."""
    try:
        task = Task.get(task_id)
    except RecordNotFound:
        tid = str_task_id(task_id)
        raise ValueError(f"Task not found: {tid}")

    return task


def print_done(msg, task):
    """Print a message with the task id and title."""
    tid = str_task_id(task.id)
    print(f"✓ {msg} | Id: {tid} | Title: {task.title}")


def add_event_row(event, grid, multi_day, habit_lookup=None):
    """Format and add an event to a Rich table grid."""
    if event.get("dateMode") == "ALL_DAY":
        return

    title = event.get("title") or "Untitled"

    event_date = event.get("eventDate") or {}
    event_start = parse_event_time(event_date.get("start"))
    event_end = parse_event_time(event_date.get("end"))

    reclaim_data = event.get("reclaimData") or {}
    resource_id = reclaim_data.get("reclaimResourceId") or {}
    if resource_id.get("type") == "SmartSeriesId" and habit_lookup:
        habit_id = habit_lookup.get(title)
        event_id = (
            "h" + str_tid(scramble_id(habit_id)).zfill(5) if habit_id else "."
        )
    else:
        event_id = str_event_id(event)

    if event_start and event_end:
        duration = str_duration(
            int((event_end - event_start).total_seconds() / 60)
        )
    else:
        duration = ""

    row = [str_event_color(event), event_id]
    if multi_day:
        row.append(event_start.strftime("%Y-%m-%d") if event_start else "")
    row.append(event_start.strftime("%H:%M") if event_start else "")
    row.append(duration)
    row.append(str_event_type(event))
    row.append(title)

    grid.add_row(*row)
