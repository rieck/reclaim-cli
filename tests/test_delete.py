# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Test cases for delete command

import pytest
from reclaim_sdk.resources.task import Task
from reclaim.utils import id_to_str, get_task

def test_delete_task(setup_reclaim, commands):
    # Create a test task first
    task = Task(title="Test task")
    task.save()
    task_id = id_to_str(task.id)

    # Get delete-task command
    cmd = next(cmd for cmd in commands if cmd.name == "delete-task")
    args = type('Args', (), {'id': task_id})
    cmd.run(args)

    # Verify task is deleted
    with pytest.raises(Exception):
        get_task(task_id)
