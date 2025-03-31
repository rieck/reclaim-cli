import pytest
from reclaim.commands import load
from reclaim.utils import set_api_key, id_to_str
from reclaim_sdk.resources.task import Task


@pytest.fixture
def commands():
    """Return all available Reclaim CLI commands."""
    set_api_key({})
    return {cmd.name: cmd for cmd in load()}


@pytest.fixture
def test_task():
    """Create and yield a test task, cleaning up afterwards."""
    # Create task
    task = Task(title="Test task")
    tid = id_to_str(task.id)
    task.save()
    yield tid

    # Cleanup
    try:
        task.delete()
    except Exception:
        pass
