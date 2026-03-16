"""Test cases for delete command.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import argparse
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from reclaim_sdk.resources.task import TaskStatus

from reclaim.str import (
    _resolve_color,
    str_event_color,
    str_event_type,
    str_habit_id,
    str_task_id,
    str_task_state,
)
from reclaim.utils import get_task


def test_delete_task(commands, test_task):
    """Test delete-task command."""
    args = argparse.Namespace(id=test_task)

    # Validate and run
    cmd = commands["delete-task"]
    cmd.validate_args(args)
    cmd.run(args)

    # Verify task is deleted
    with pytest.raises(ValueError):
        get_task(args.id)


def test_mark_task(commands, test_task):
    """Test mark-task command."""
    args = argparse.Namespace(id=test_task, mark="complete")

    # Validate and run
    cmd = commands["mark-task"]
    cmd.validate_args(args)
    cmd.run(args)

    # Wait for task to be updated
    time.sleep(3)

    # Verify task is complete
    task = get_task(args.id)
    assert task.status == TaskStatus.ARCHIVED
    # No need to delete task


def test_create_task(commands):
    """Test create-task command."""
    args = argparse.Namespace(
        title="Test Task",
        due="in 7 days",
        snooze_until="in 2 days",
        priority="P3",
        duration="2h15m",
        min_chunk_size="1h",
        max_chunk_size="2h",
        notes="Some notes",
    )

    # Validate and run
    cmd = commands["create-task"]
    cmd.validate_args(args)
    task = cmd.run(args)

    time.sleep(3)

    task = get_task(task.id)
    assert task.title == args.title
    assert task.priority == args.priority
    assert task.duration == args.duration / 60
    assert task.min_chunk_size == args.min_chunk_size / 15
    assert task.max_chunk_size == args.max_chunk_size / 15

    # Timezones drive me mad.
    # assert task.due in [args.due, args.due.replace(tzinfo=task.due.tzinfo)]

    # Snooze time is matched to chunks. So round it up to next 15 min block
    rounded_minutes = ((args.snooze_until.minute + 14) // 15) * 15
    delta_minutes = rounded_minutes - args.snooze_until.minute
    args.snooze_until = args.snooze_until + timedelta(minutes=delta_minutes)
    args.snooze_until = args.snooze_until.replace(second=0, microsecond=0)

    # assert task.snooze_until in [
    #    args.snooze_until,
    #    args.snooze_until.replace(tzinfo=task.snooze_until.tzinfo),
    # ]

    # Remove task
    task.delete()


def test_show_task(commands, test_task):
    """Test show-task command with a valid task ID."""
    args = argparse.Namespace(id=test_task)
    cmd = commands["show-task"]
    cmd.validate_args(args)
    task = cmd.run(args)
    assert task.title == "Test task"


def test_show_task_with_notes(commands, test_task_with_notes):
    """Test show-task command displays notes when present."""
    args = argparse.Namespace(id=test_task_with_notes)
    cmd = commands["show-task"]
    cmd.validate_args(args)
    task = cmd.run(args)
    assert task.notes == "Some test notes"


def test_show_task_invalid(commands):
    """Test show-task command with an unknown task ID."""
    args = argparse.Namespace(id="t00000")
    cmd = commands["show-task"]
    cmd.validate_args(args)
    with pytest.raises(ValueError):
        cmd.run(args)


def test_list_tasks_default(commands):
    """Test list-tasks command with default args."""
    args = argparse.Namespace(
        status="active", all=False, due=None, at_risk=False, order="due"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    tasks = cmd.run(args)
    assert isinstance(tasks, list)


def test_list_tasks_all(commands):
    """Test list-tasks command with --all flag."""
    args = argparse.Namespace(
        status="active", all=True, due=None, at_risk=False, order="due"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    tasks = cmd.run(args)
    assert isinstance(tasks, list)


def test_list_tasks_order_title(commands):
    """Test list-tasks command ordered by title."""
    args = argparse.Namespace(
        status="active", all=True, due=None, at_risk=False, order="title"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    tasks = cmd.run(args)
    titles = [t.title for t in tasks]
    assert titles == sorted(titles)


def test_list_tasks_order_id(commands):
    """Test list-tasks command ordered by id."""
    args = argparse.Namespace(
        status="active", all=True, due=None, at_risk=False, order="id"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    tasks = cmd.run(args)
    ids = [t.id for t in tasks]
    assert ids == sorted(ids)


def test_list_tasks_status_filter(commands):
    """Test list-tasks command with explicit status filter."""
    args = argparse.Namespace(
        status="new", all=False, due=None, at_risk=False, order="due"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    tasks = cmd.run(args)
    assert isinstance(tasks, list)


def test_list_tasks_invalid_status(commands):
    """Test list-tasks command rejects invalid status."""
    args = argparse.Namespace(
        status="bogus", all=False, due=None, at_risk=False, order="due"
    )
    cmd = commands["list-tasks"]
    with pytest.raises(ValueError):
        cmd.validate_args(args)


def test_list_tasks_invalid_order(commands):
    """Test list-tasks command rejects invalid order field."""
    args = argparse.Namespace(
        status="active", all=False, due=None, at_risk=False, order="bogus"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    with pytest.raises(ValueError):
        cmd.run(args)


def test_list_tasks_at_risk(commands):
    """Test list-tasks command with --at-risk filter."""
    args = argparse.Namespace(
        status="active", all=False, due=None, at_risk=True, order="due"
    )
    cmd = commands["list-tasks"]
    cmd.validate_args(args)
    tasks = cmd.run(args)
    assert all(t.at_risk for t in tasks)


def test_list_events_default(commands):
    """Test list-events command with default args (today)."""
    args = argparse.Namespace(date=None, future=None)
    cmd = commands["list-events"]
    cmd.validate_args(args)
    events = cmd.run(args)
    assert isinstance(events, list)


def test_list_events_future(commands):
    """Test list-events command with future days."""
    args = argparse.Namespace(date=None, future=3)
    cmd = commands["list-events"]
    cmd.validate_args(args)
    events = cmd.run(args)
    assert isinstance(events, list)
    starts = [(e.get("eventDate") or {}).get("start", "") for e in events]
    assert starts == sorted(starts)


def test_list_events_invalid_future(commands):
    """Test list-events command rejects future < 1."""
    args = argparse.Namespace(date=None, future=0)
    cmd = commands["list-events"]
    with pytest.raises(ValueError):
        cmd.validate_args(args)


def test_list_events_date(commands):
    """Test list-events command with a specific date."""
    args = argparse.Namespace(date="tomorrow", future=None)
    cmd = commands["list-events"]
    cmd.validate_args(args)
    events = cmd.run(args)
    assert isinstance(events, list)


def test_show_habit(commands, test_habit):
    """Test show-habit command with a valid habit ID."""
    args = argparse.Namespace(id=test_habit)
    cmd = commands["show-habit"]
    cmd.validate_args(args)
    habit = cmd.run(args)
    assert "title" in habit
    assert "id" in habit


def test_show_habit_invalid(commands):
    """Test show-habit command with an unknown habit ID."""
    args = argparse.Namespace(id="h00000")
    cmd = commands["show-habit"]
    cmd.validate_args(args)
    with pytest.raises(ValueError):
        cmd.run(args)


def test_edit_task(commands, test_task):
    """Test edit-task command."""
    args = argparse.Namespace(
        id=test_task,
        title="Test Task",
        due="in 7 days",
        snooze_until="in 2 days",
        priority="P3",
        duration="4h",
        min_chunk_size="1h",
        max_chunk_size="2h",
        notes="Some notes",
    )

    # Validate and run
    cmd = commands["edit-task"]
    cmd.validate_args(args)
    task = cmd.run(args)

    time.sleep(3)

    task = get_task(task.id)
    assert task.title == args.title
    # assert task.due in [args.due, args.due.replace(tzinfo=task.due.tzinfo)]
    assert task.priority == args.priority
    assert task.duration == args.duration / 60
    assert task.min_chunk_size == args.min_chunk_size / 15
    assert task.max_chunk_size == args.max_chunk_size / 15

    # Snooze time is matched to chunks. So round it up to next 15 min block
    rounded_minutes = ((args.snooze_until.minute + 14) // 15) * 15
    delta_minutes = rounded_minutes - args.snooze_until.minute
    args.snooze_until = args.snooze_until + timedelta(minutes=delta_minutes)
    args.snooze_until = args.snooze_until.replace(second=0, microsecond=0)

    # assert task.snooze_until in [
    #    args.snooze_until,
    #    args.snooze_until.replace(tzinfo=task.snooze_until.tzinfo),
    # ]
    # No need to delete task


# --- _resolve_color ---


def test_resolve_color_name():
    """Named Google Calendar colors resolve to their hex value."""
    assert _resolve_color("SAGE") == "#33B679"
    assert _resolve_color("sage") == "#33B679"
    assert _resolve_color("TOMATO") == "#D50000"


def test_resolve_color_hex_passthrough():
    """Hex strings are passed through unchanged."""
    assert _resolve_color("#AABBCC") == "#AABBCC"


def test_resolve_color_none_string():
    """The API sentinel 'NONE' returns the default."""
    assert _resolve_color("NONE") == ""
    assert _resolve_color("NONE", "#808080") == "#808080"


def test_resolve_color_empty():
    """Empty and None inputs return the default."""
    assert _resolve_color("") == ""
    assert _resolve_color(None, "#808080") == "#808080"


def test_resolve_color_unknown():
    """Unknown non-hex strings return the default."""
    assert _resolve_color("NOTACOLOR") == ""
    assert _resolve_color("NOTACOLOR", "#808080") == "#808080"


# --- str_event_color ---

_USER_EVENT = {
    "calendarId": 42,
    "color": None,
    "reclaimData": {"reclaimEventType": "USER"},
}

_HABIT_EVENT = {
    "color": "SAGE",
    "reclaimData": {"reclaimEventType": "SMART_HABIT"},
}


def test_event_color_user_with_calendar():
    """USER event uses the calendar config color."""
    calendars = {42: {"color": "banana"}}
    dot = str_event_color(_USER_EVENT, calendars)
    assert "#F6BF26" in dot


def test_event_color_user_no_calendar():
    """USER event without calendar config falls back to gray."""
    dot = str_event_color(_USER_EVENT, None)
    assert "#808080" in dot


def test_event_color_habit():
    """Habit event uses the API color."""
    dot = str_event_color(_HABIT_EVENT)
    assert "#33B679" in dot


def test_event_color_none_api_color():
    """API color 'NONE' falls back to gray dot."""
    event = {
        "color": "NONE",
        "reclaimData": {"reclaimEventType": "SMART_HABIT"},
    }
    dot = str_event_color(event)
    assert "#808080" in dot


# --- str_event_type ---


def test_event_type_colored_user():
    """USER event type string is colored with calendar color."""
    calendars = {42: {"color": "banana"}}
    label = str_event_type(_USER_EVENT, calendars)
    assert "#F6BF26" in label
    assert "U" in label


def test_event_type_uncolored():
    """Event type without a color has no markup."""
    event = {
        "color": "NONE",
        "reclaimData": {
            "reclaimEventType": "TASK_ASSIGNMENT",
            "priority": "P3",
        },
    }
    label = str_event_type(event)
    assert label == "T3"


# --- str_task_state ---


def _make_task(at_risk=False, due=None, status="SCHEDULED", priority="P3"):
    """Build a minimal task-like namespace for str_task_state."""
    return SimpleNamespace(
        at_risk=at_risk,
        due=due,
        status=status,
        priority=priority,
        deferred=False,
        deleted=False,
        adjusted=False,
    )


def test_task_state_normal():
    """Normal task state has no color markup."""
    state = str_task_state(_make_task())
    assert "[" not in state


def test_task_state_at_risk():
    """At-risk task state is colored yellow (BANANA)."""
    state = str_task_state(_make_task(at_risk=True))
    assert "#F6BF26" in state


def test_task_state_overdue():
    """Overdue task state is colored red (TOMATO)."""
    past = datetime(2000, 1, 1, tzinfo=timezone.utc)
    state = str_task_state(_make_task(due=past))
    assert "#D50000" in state


def test_task_state_overdue_beats_at_risk():
    """Overdue takes priority over at-risk coloring."""
    past = datetime(2000, 1, 1, tzinfo=timezone.utc)
    state = str_task_state(_make_task(at_risk=True, due=past))
    assert "#D50000" in state
    assert "#F6BF26" not in state


# --- str_habit_id / str_task_id roundtrip ---


def test_habit_id_prefix():
    """Habit IDs start with 'h'."""
    assert str_habit_id(12345).startswith("h")


def test_task_id_prefix():
    """Task IDs start with 't'."""
    assert str_task_id(12345).startswith("t")


def test_habit_task_id_same_suffix():
    """Habit and task IDs for the same integer share the same suffix."""
    assert str_habit_id(12345)[1:] == str_task_id(12345)[1:]


# --- config command ---


def test_config_command(commands):
    """Config command runs without error."""
    cmd = commands["config"]
    cmd.run(argparse.Namespace())
