import argparse

import pytest
from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.resources.task import Task

from reclaim.commands import load
from reclaim.str import str_task_id
from reclaim.utils import load_config, set_api_key


@pytest.fixture
def commands():
    """Return all available Reclaim CLI commands."""
    args = argparse.Namespace(
        config="~/.reclaim-dev",
    )
    args = load_config(args)
    set_api_key(args)
    return {cmd.name: cmd for cmd in load()}


@pytest.fixture
def test_task():
    """Create and yield a test task, cleaning up afterwards."""
    task = Task(title="Test task")
    task.save()
    yield str_task_id(task.id)

    try:
        task.delete()
    except Exception:
        pass


@pytest.fixture
def test_task_with_notes():
    """Create and yield a test task with notes, cleaning up afterwards."""
    task = Task(title="Test task with notes", notes="Some test notes")
    task.save()
    yield str_task_id(task.id)

    try:
        task.delete()
    except Exception:
        pass


@pytest.fixture
def test_habit(commands):
    """Return a valid habit display ID for testing."""
    habits = ReclaimClient().get("/api/assist/habits/daily")
    if not habits:
        pytest.skip("No habits available for testing")
    habit = habits[0]
    return "h" + str_task_id(habit["id"])[1:]
