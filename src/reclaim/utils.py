"""Utility Functions.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import argparse
import os

import yaml
from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.exceptions import RecordNotFound
from reclaim_sdk.resources.task import Task

from .str import str_tid


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Custom help formatter with fixed width and position."""

    def __init__(self, prog):
        """Initialize the help formatter."""
        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 80  # fallback if terminal size can't be determined
        super().__init__(prog, max_help_position=16, width=width)

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = "usage: "

        # Only modify main command usage, not subcommands
        if self._prog == "reclaim":  # Check if we're formatting main command
            # Find the subparser action
            subparser_action = None
            for action in actions:
                if isinstance(action, argparse._SubParsersAction):
                    subparser_action = action
                    break

            if subparser_action:
                # Use <command> instead of listing all commands
                return f"{prefix}{self._prog} [options] <command> ...\n\n"

        # For subcommands, use default usage formatting
        return super()._format_usage(usage, actions, groups, prefix)

    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            # Get the original format but remove the first line
            parts = super()._format_action(action).split("\n")
            return "\n".join(parts[1:])
        return super()._format_action(action)


def load_config(args):
    """Load configuration file."""
    args.config = os.path.expanduser(args.config)
    if not os.path.exists(args.config):
        return args

    with open(args.config) as f:
        config = yaml.safe_load(f)
        for key, value in config.items():
            setattr(args, key, value)

    return args


def set_api_key(cfg):
    """Set the API key in the configuration file."""
    token = None
    if os.environ.get("RECLAIM_TOKEN"):
        token = os.environ.get("RECLAIM_TOKEN")
    elif hasattr(cfg, "reclaim_token"):
        token = cfg.reclaim_token
    if not token:
        raise Exception("No Reclaim API token set")
    ReclaimClient.configure(token=token)


def get_task(task_id):
    """Get a task from Reclaim.ai."""
    try:
        task = Task.get(task_id)
    except RecordNotFound:
        tid = str_tid(task_id)
        raise ValueError(f"Task not found: {tid}")

    return task


def print_done(msg, task):
    """Print a message with the task id and title."""
    tid = str_tid(task.id)
    print(f"✓ {msg} | Id: {tid} | Title: {task.title}")
