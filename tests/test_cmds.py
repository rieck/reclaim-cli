# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Test cases for delete command

import argparse
import time

import pytest
from reclaim_sdk.resources.task import TaskStatus

from reclaim.utils import get_task, id_to_str


def test_delete_task(commands, test_task):
    """Test delete-task command"""
    args = argparse.Namespace(id=test_task)

    # Validate and run
    cmd = commands["delete-task"]
    cmd.validate_args(args)
    cmd.run(args)

    # Verify task is deleted
    with pytest.raises(Exception):
        get_task(args.id)


def test_mark_task(commands, test_task):
    """Test mark-task command"""
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


def test_create_task(commands):
    """Test create-task command"""
    args = argparse.Namespace(
        title="Test Task",
        due="in 7 days",
        snooze_until="in 2 days",
        priority="P3",
        duration="2h15",
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
    assert task.due == args.due
    assert task.snooze_until == args.snooze_until
    assert task.priority == args.priority
    assert task.duration == args.duration
    assert task.min_chunk_size == args.min_chunk_size
    assert task.max_chunk_size == args.max_chunk_size

    # Remove task
    task.delete()
