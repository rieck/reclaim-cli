"""Test cases for delete command.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import argparse
import time
from datetime import timedelta

import pytest
from reclaim_sdk.resources.task import TaskStatus

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
    time.sleep(1)

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

    time.sleep(1)

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

    time.sleep(1)

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
