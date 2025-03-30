# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Utility functions

import yaml
import os
import argparse
import re
from rich.table import Table
from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.resources.task import Task, TaskStatus
from reclaim_sdk.exceptions import RecordNotFound


# Base36 character set
ID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Custom help formatter with fixed width and position."""

    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = 'usage: '

        # Find the subparser action
        subparser_action = None
        for action in actions:
            if isinstance(action, argparse._SubParsersAction):
                subparser_action = action
                break

        if subparser_action:
            # Use <command> instead of listing all commands
            usage = f"{prefix}{self._prog} [options] <command> ...\n\n"

        return usage

    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            # Get the original format but remove the first line
            parts = super()._format_action(action).split('\n')
            return '\n'.join(parts[1:])
        return super()._format_action(action)


def load_config(args):
    """Load configuration file"""
    if not os.path.exists(args.config):
        return args

    with open(args.config) as f:
        config = yaml.safe_load(f)
        for key, value in config.items():
            setattr(args, key, value)

    return args


def set_api_key(cfg):
    """Set the API key in the configuration file."""
    token = getattr(cfg, 'reclaim_token',
                    None) or os.environ.get('RECLAIM_TOKEN')
    if not token:
        raise Exception("No Reclaim API token set")
    ReclaimClient.configure(token=token)


def id_to_str(task_id):
    """Convert an identifier to a short string."""
    if task_id == 0:
        return "0"

    result = ""
    while task_id:
        task_id, remainder = divmod(task_id, len(ID_CHARS))
        result = ID_CHARS[remainder] + result
    return result


def str_to_id(encoded):
    """Convert a string to an identifier."""
    if not all(c in ID_CHARS for c in encoded):
        raise ValueError(f"Invalid characters in ID {encoded}")
    try:
        return int(encoded, len(ID_CHARS))
    except ValueError:
        raise ValueError(f"Cannot decode ID {encoded}")


def str_to_list(str_list):
    """Convert a string to a list."""
    return [s.strip() for s in str_list.split(",")] if str_list else []


def get_task(task_id):
    """Get a task from Reclaim.ai"""
    try:
        task = Task.get(task_id)
    except RecordNotFound:
        tid = id_to_str(task_id)
        raise ValueError(f"Task not found: {tid}")

    return task


def print_done(msg, task):
    """Print a message with the task id and title."""
    tid = id_to_str(task.id)
    print(f"✓ {msg} | Id: {tid} | Title: {task.title}")


def str_duration(minutes):
    """Convert minutes to a duration string"""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h{minutes}m"


def parse_duration(time_str):
    """Parse a duration string into minutes """
    time_str = time_str.lower().replace(' ', '')

    # Define regex patterns for time units
    patterns = [
        # matches "XXhrs", "XXhr", "XXh", or "XXhours"
        ([60], r'(\d+)(?:hr(s)?|h|hours)'),
        # matches "XXmin" or "XXm"
        ([1], r'(\d+)(?:minute(s)?|min|m)'),
        ([60, 1], r'(\d+):(\d+)'),
        ([1], r'(\d+)'),
    ]

    minutes = 0
    for units, pattern in patterns:
        match = re.search(pattern, time_str)
        if not match:
            continue

        # Loop over units and groups
        groups = match.groups()
        for i, unit in enumerate(units):
            minutes += unit * int(groups[i])
        time_str = re.sub(pattern, '', time_str)

    if minutes <= 0:
        raise ValueError("No or negative duration")

    return minutes


def str_task_status(task):
    """Convert a task status to a string."""

    # Get status character
    if task.status == TaskStatus.CANCELLED:
        status = 'X'
    else:
        status = task.status[0]

    # Get priority digit
    prio = task.priority[1]

    # Build status indicators
    extra = "".join([
        "!" if task.at_risk else "",
        ">" if task.deferred else "",
        "-" if task.deleted else "",
        "~" if task.adjusted else "",
    ])

    return f"{status}{prio}{extra}"
