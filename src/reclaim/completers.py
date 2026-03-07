"""Shell completion functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import argparse


def _setup_auth():
    """Load config and set up API authentication for completion."""
    from reclaim.utils import load_config, set_api_key

    try:
        args = argparse.Namespace(config="~/.reclaim")
        args = load_config(args)
        set_api_key(args)
        return True
    except Exception:
        return False


def task_ids(**kwargs):
    """Return active task display IDs for shell completion."""
    if not _setup_auth():
        return []
    try:
        from reclaim_sdk.resources.task import Task, TaskStatus

        from reclaim.str import str_task_id

        active = {TaskStatus.NEW, TaskStatus.SCHEDULED, TaskStatus.IN_PROGRESS}
        return [str_task_id(t.id) for t in Task.list() if t.status in active]
    except Exception:
        return []


def habit_ids(**kwargs):
    """Return habit display IDs for shell completion."""
    if not _setup_auth():
        return []
    try:
        from reclaim_sdk.client import ReclaimClient

        from reclaim.str import str_task_id

        habits = ReclaimClient().get("/api/assist/habits/daily")
        return ["h" + str_task_id(h["id"])[1:] for h in habits]
    except Exception:
        return []
