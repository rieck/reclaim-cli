"""String Functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from reclaim_sdk.resources.task import TaskStatus

# Base36 character set
ID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"

# Bijective scrambling on [0, 36^5): multiply by a constant coprime to 36^5.
# 36^5 = 2^10 * 3^10, so any multiplier not divisible by 2 or 3 is coprime.
_ID_MOD = 36**5  # 60_466_176
_ID_MUL = 17_364_421  # prime, not divisible by 2 or 3
_ID_INV = pow(_ID_MUL, -1, _ID_MOD)  # modular inverse


def scramble_id(n):
    """Bijectively scramble n within [0, 36^5)."""
    return (n * _ID_MUL) % _ID_MOD


def unscramble_id(n):
    """Reverse scramble_id."""
    return (n * _ID_INV) % _ID_MOD


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


def str_event_id(event):
    """Convert an event resource ID to a compact prefixed string."""
    reclaim_data = event.get("reclaimData") or {}
    resource_id = reclaim_data.get("reclaimResourceId") or {}
    id_type = resource_id.get("type")

    if id_type == "TaskId":
        return "t" + str_tid(scramble_id(resource_id["id"])).zfill(5)
    elif id_type == "SmartSeriesId":
        return "h" + str_tid(scramble_id(resource_id["seriesId"])).zfill(5)
    elif id_type == "SchedulingLinkId":
        numeric = int(resource_id["id"].replace("-", "")[:6], 16)
        return "m" + str_tid(scramble_id(numeric)).zfill(5)
    return ""


# Google Calendar color name → hex
_EVENT_COLORS = {
    "TOMATO": "#D50000",
    "FLAMINGO": "#E67C73",
    "TANGERINE": "#F4511E",
    "BANANA": "#F6BF26",
    "SAGE": "#33B679",
    "BASIL": "#0B8043",
    "PEACOCK": "#039BE5",
    "BLUEBERRY": "#3F51B5",
    "LAVENDER": "#7986CB",
    "GRAPE": "#8E24AA",
    "GRAPHITE": "#616161",
}


def _color_dot(color):
    """Return a Rich-markup colored dot for a color name."""
    hex_color = _EVENT_COLORS.get(color or "", "#808080")
    return f"[{hex_color}]●[/{hex_color}]"


def str_event_color(event, calendars=None):
    """Return a colored dot for an event."""
    color = event.get("color")
    if not color:
        reclaim_data = event.get("reclaimData") or {}
        if reclaim_data.get("reclaimEventType") == "USER":
            cal_id = str(event.get("calendarId", ""))
            cal_info = (
                (calendars or {}).get(int(cal_id))
                or (calendars or {}).get(cal_id)
                or {}
            )
            raw = cal_info.get("color") or ""
            hex_color = _EVENT_COLORS.get(raw.upper()) or raw or "#808080"
            return f"[{hex_color}]●[/{hex_color}]"
    return _color_dot(color)


def str_task_color(task):
    """Return a colored dot for a task."""
    color = getattr(task, "event_color", None)
    return _color_dot(color.value if color else None)


def str_event_type(event):
    """Convert an event type and priority to a compact string."""
    type_chars = {
        "TASK_ASSIGNMENT": "T",
        "SMART_HABIT": "H",
        "SCHEDULING_LINK_MEETING": "M",
        "ONE_ON_ONE": "O",
        "CONFERENCE_BUFFER": "C",
        "USER": "U",
    }

    reclaim_data = event.get("reclaimData") or {}
    event_type = reclaim_data.get("reclaimEventType", "")
    priority = reclaim_data.get("priority", "")

    type_char = type_chars.get(event_type, "E")
    prio_digit = priority[1] if len(priority) == 2 else ""

    return f"{type_char}{prio_digit}"


def str_tid(task_id):
    """Convert an identifier to a base36 string."""
    if task_id == 0:
        return "0"

    result = ""
    while task_id:
        task_id, remainder = divmod(task_id, len(ID_CHARS))
        result = ID_CHARS[remainder] + result
    return result


def str_task_id(task_id):
    """Convert a task identifier to a prefixed display string."""
    return "t" + str_tid(scramble_id(task_id)).zfill(5)
