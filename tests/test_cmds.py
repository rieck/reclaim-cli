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


def test_edit_task(commands, test_task):
    """Test edit-task command."""
    args = argparse.Namespace(
        id=test_task,
        title="Test Task",
        due="in 7 days",
        snooze_until="in 2 days",
        priority="P3",
        duration="2h30m",
        min_chunk_size="1h",
        max_chunk_size="2h",
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
