import argparse

import pytest
from reclaim_sdk.resources.task import Task

from reclaim.commands import load
from reclaim.utils import id_to_str, load_config, set_api_key


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
    # Create task
    task = Task(title="Test task")
    task.save()
    yield id_to_str(task.id)

    # Cleanup
    try:
        task.delete()
    except Exception:
        pass
