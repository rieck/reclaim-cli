import os
import pytest
from reclaim.commands import load
from reclaim.utils import set_api_key


@pytest.fixture
def setup_reclaim():
    """Setup Reclaim API key"""
    set_api_key({})

@pytest.fixture
def commands():
    """Return all commands"""
    return load()
