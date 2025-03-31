# Reclaim CLI
# Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
# ---
# Test cases for delete command

import pytest
from reclaim.utils import get_task


def test_delete_task(commands, test_task):
    """ Test delete-task command """
    tid = test_task
    cmd = commands['delete-task']

    # Run command
    args = type('Args', (), {'id': tid})
    cmd.run(args)

    # Verify task is deleted
    with pytest.raises(Exception):
        get_task(tid)
