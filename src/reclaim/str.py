"""String Functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import os
import select
import sys
import termios
import tty

from reclaim_sdk.resources.task import TaskStatus


def is_dark_terminal():
    """Detect whether the terminal has a dark background.

    Tries two methods in order:
    1. OSC 11 escape sequence - queries the terminal for its actual background
       color (requires a real TTY, times out after 0.1s if unsupported).
    2. $COLORFGBG env var - set by some terminals (rxvt, konsole, etc.) in
       "fg;bg" format where bg < 8 means dark.

    Returns True for dark, False for light, None if undetermined.
    """
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                sys.stdout.write("\033]11;?\033\\")
                sys.stdout.flush()
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    response = ""
                    while select.select([sys.stdin], [], [], 0.05)[0]:
                        response += sys.stdin.read(1)
                    if "rgb:" in response:
                        rgb_part = response.split("rgb:")[1].rstrip("\\\x1b\a")
                        r, g, b = (int(c[:2], 16) for c in rgb_part.split("/"))
                        return (r + g + b) < 384  # 128 * 3
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass

    colorfgbg = os.environ.get("COLORFGBG", "")
    if colorfgbg:
        try:
            return int(colorfgbg.split(";")[-1]) < 8
        except ValueError:
            pass

    return None


def _brighten(hex_color, amount=50):
    """Brighten a hex color by adding a fixed amount to each channel."""
    h = hex_color.lstrip("#")
    r = min(255, int(h[0:2], 16) + amount)
    g = min(255, int(h[2:4], 16) + amount)
    b = min(255, int(h[4:6], 16) + amount)
    return f"#{r:02X}{g:02X}{b:02X}"


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

_DARK_TERMINAL = is_dark_terminal()
if _DARK_TERMINAL:
    _EVENT_COLORS = {k: _brighten(v) for k, v in _EVENT_COLORS.items()}


def _resolve_color(raw, default=""):
    """Resolve a Google Calendar color name or hex string to a hex value."""
    if not raw or raw.upper() == "NONE":
        return default
    return _EVENT_COLORS.get(raw.upper()) or (
        raw if raw.startswith("#") else default
    )


def _color_dot(hex_color):
    """Return a Rich-markup colored dot for a hex color."""
    c = hex_color or "#808080"
    return f"[{c}]●[/{c}]"


def _event_hex_color(event, calendars=None):
    """Return the hex color for an event, empty string if uncolored."""
    reclaim_data = event.get("reclaimData") or {}
    if reclaim_data.get("reclaimEventType") == "USER":
        cal_id = str(event.get("calendarId", ""))
        cal_info = (
            (calendars or {}).get(int(cal_id))
            or (calendars or {}).get(cal_id)
            or {}
        )
        return _resolve_color(cal_info.get("color"), "#808080")
    return _resolve_color(event.get("color"))


def str_event_color(event, calendars=None):
    """Return a colored dot for an event."""
    return _color_dot(_event_hex_color(event, calendars))


def str_task_color(task):
    """Return a colored dot for a task."""
    color = getattr(task, "event_color", None)
    return _color_dot(
        _resolve_color(color.value if color else None, "#808080")
    )


def str_event_type(event, calendars=None):
    """Convert an event type and priority to a compact colored string."""
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
    label = f"{type_char}{prio_digit}"

    hex_color = _event_hex_color(event, calendars)
    if not hex_color:
        return label
    return f"[{hex_color}]{label}[/{hex_color}]"


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


def str_habit_id(habit_id):
    """Convert a habit identifier to a prefixed display string."""
    return "h" + str_tid(scramble_id(habit_id)).zfill(5)


def str_task_state(task):
    """Return the task state string, colored by urgency."""
    from datetime import datetime, timezone

    state = str_task_status(task)
    if task.due and task.due < datetime.now(timezone.utc):
        c = _EVENT_COLORS["TOMATO"]
    elif task.at_risk:
        c = _EVENT_COLORS["BANANA"]
    else:
        return state
    return f"[{c}]{state}[/{c}]"
