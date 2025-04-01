# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Test cases for delete command

import pytest
import time
import argparse
from reclaim_sdk.resources.task import Task, TaskStatus
from reclaim.utils import get_task, str_to_id


def test_delete_task(commands, test_task):
    """ Test delete-task command """
    args = argparse.Namespace(
        id=test_task
    )

    # Validate and run
    cmd = commands['delete-task']
    cmd.validate_args(args)
    cmd.run(args)

    # Verify task is deleted
    with pytest.raises(Exception):
        get_task(args.id)

def test_mark_task(commands, test_task):
    """ Test mark-task command """
    args = argparse.Namespace(
        id=test_task,
        mark="complete"
    )

    # Validate and run
    cmd = commands['mark-task']
    cmd.validate_args(args)
    task =cmd.run(args)

    # Wait for task to be updated
    time.sleep(1)

    # Verify task is complete
    task = get_task(args.id)
    assert task.status == TaskStatus.ARCHIVED
