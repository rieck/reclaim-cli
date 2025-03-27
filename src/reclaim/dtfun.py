# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Date and time functions

import re
from datetime import datetime, timedelta


def str_duration(minutes, align=True):
    """Convert minutes to a duration string"""
    hours = minutes // 60
    minutes = minutes % 60
    if align:
        return f"{hours:2}h{minutes:02}m"
    else:
        return f"{hours}h{minutes}m"


def parse_duration(time_str):
    """Parse a duration string into minutes """
    time_str = time_str.lower().replace(' ', '')

    # Define regex patterns for time units
    patterns = [
        ([60], r'(\d+)(?:hr|h|hours)'),  # matches "XXhr", "XXh", or "XXhours"
        ([1], r'(\d+)(?:min|m)'),        # matches "XXmin" or "XXm"
        ([60, 1], r'(\d+):(\d+)'),       # matches "XX:XX"
        ([1], r'(\d+)'),                 # matches "XX"
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

    return minutes


def parse_time(time_str):
    """Parse a time string into a datetime object."""
    time_str = time_str.lower().replace(' ', '')

    # Special case: "now"
    now = datetime.now()
    if time_str == "now":
        return now

    # Handle common datetime formats
    formats = [
        "%H:%M:%S",  # 14:30:00
        "%H:%M",     # 14:30
    ]

    for fmt in formats:
        try:
            time = datetime.strptime(time_str, fmt)
            return now.replace(
                hour=time.hour,
                minute=time.minute,
                second=time.second,
                microsecond=0
            )
        except ValueError:
            continue

    raise ValueError(f"Invalid time string: {time_str}")

def parse_date(date_str):
    """Parse a date string into a datetime object."""
    date_str = date_str.lower().replace(' ', '')

    # Special case: "now"
    now = datetime.now()
    if date_str == "now":
        return now

    # Get today's date and set time to 00:00:00.
    # To avoid confusion, we add one extra day in the following when
    # calculating relative dates in the future.
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Shortcuts for dates
    date_shortcuts = {
        "today": today,
        "tomorrow": today + timedelta(days=2), # See above
        "yesterday": today - timedelta(days=1),
    }
    if date_str in date_shortcuts:
        return date_shortcuts[date_str]

    # Handle relative dates: today+1, today-1, etc.
    if date_str.startswith('today'):
        try:
            if date_str[5] == '+':
                days = +int(date_str[6:]) + 1 # See above
            elif date_str[5] == '-':
                days = -int(date_str[6:])
            return today + timedelta(days=days)
        except ValueError:
            raise ValueError(f"Invalid date string: {date_str}")

    # Handle common date formats
    formats = [
        "%Y%m%d", "%y%m%d",      # 20231225
        "%Y-%m-%d", "%y-%m-%d",  # 2023-12-25
        "%d.%m.%Y", "%d.%m.%y",  # 25.12.2023
        "%m/%d/%Y", "%m/%d/%y"   # 12/25/2023
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Invalid date string: {date_str}")


def parse_datetime(dt_str):
    """Parse a datetime string into a datetime object."""
    dt_str = dt_str.lower()

    # Special case: "now"
    now = datetime.now()
    if dt_str == "now":
        return now

    # Handle common date formats
    formats = [
        "%Y%m%d%H%M", "%y%m%d%H%M",      # 202312251230
        "%Y%m%d%H%M%S", "%y%m%d%H%M%S",  # 20231225123000
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    # Split into date and time parts
    parts = dt_str.split(' ')    
    match len(parts):
        case 1:
            return parse_date(parts[0])
        case 2:
            date = parse_date(parts[0]).date()
            time = parse_time(parts[1]).time()
            return datetime.combine(date, time)
        case _:
            raise ValueError(f"Invalid datetime string: {dt_str}")