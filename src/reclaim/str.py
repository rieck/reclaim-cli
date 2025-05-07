"""String Functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from reclaim_sdk.resources.task import TaskStatus

# Base36 character set
ID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"


def str_duration(minutes):
    """Convert minutes to a duration string."""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h{minutes}m"


def str_task_status(task):
    """Convert a task status to a string."""
    # Get status character
    if task.status == TaskStatus.CANCELLED:
        status = "X"
    else:
        status = task.status[0]

    # Get priority digit
    prio = task.priority[1]

    # Build status indicators
    extra = "".join(
        [
            "!" if task.at_risk else "",
            ">" if task.deferred else "",
            "-" if task.deleted else "",
            "~" if task.adjusted else "",
        ]
    )

    return f"{status}{prio}{extra}"


def str_tid(task_id):
    """Convert an identifier to a short string."""
    if task_id == 0:
        return "0"

    result = ""
    while task_id:
        task_id, remainder = divmod(task_id, len(ID_CHARS))
        result = ID_CHARS[remainder] + result
    return result
