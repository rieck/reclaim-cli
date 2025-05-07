"""Parsing Functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import re

import dateparser
from reclaim_sdk.resources.task import TaskPriority

# Base36 character set
ID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"


def parse_tid(encoded):
    """Convert a string to an identifier."""
    if not all(c in ID_CHARS for c in encoded):
        raise ValueError(f"Invalid characters in ID {encoded}")
    try:
        return int(encoded, len(ID_CHARS))
    except ValueError:
        raise ValueError(f"Cannot decode ID {encoded}")


def parse_list(str_list):
    """Convert a string to a list."""
    return [s.strip() for s in str_list.split(",")] if str_list else []


def parse_duration(time_str):
    """Parse a duration string into minutes."""
    time_str = time_str.lower().replace(" ", "")

    # Define regex patterns for time units
    patterns = [
        # matches "XXhrs", "XXhr", "XXh", or "XXhours"
        ([60], r"(\d+)(?:hr(s)?|h|hours)"),
        # matches "XXmin" or "XXm"
        ([1], r"(\d+)(?:minute(s)?|min|m)"),
        ([60, 1], r"(\d+):(\d+)"),
        ([1], r"(\d+)"),
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
        time_str = re.sub(pattern, "", time_str)

    if minutes <= 0:
        raise ValueError("No or negative duration")

    return minutes


def parse_datetime(str):
    """Parse a datetime string into a datetime object."""
    dt = dateparser.parse(str)
    if not dt:
        raise ValueError(f"Invalid datetime string: {str}")
    return dt


def parse_priority(priority):
    """Parse a priority string into a priority object."""
    priority = priority.upper()
    if not priority.startswith("P"):
        priority = f"P{priority}"
    if not priority[1:].isdigit():
        raise ValueError(f"Invalid priority: {priority}")
    return TaskPriority(priority)
