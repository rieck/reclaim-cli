"""Command to show a task or habit at Reclaim.ai.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

from ..completers import habit_ids, task_ids
from .base import Command


def _all_ids(**kwargs):
    """Return task and habit IDs for shell completion."""
    return task_ids(**kwargs) + habit_ids(**kwargs)


class ShowCommand(Command):
    """Show a task or habit at Reclaim.ai."""

    name = "show"
    description = "show a task or habit"
    aliases = []

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)
        subparser.add_argument(
            "id", type=str, metavar="<id>", help="task or habit id to show"
        ).completer = _all_ids
        return subparser

    def validate_args(self, args):
        """Validate and transform command arguments."""
        args._id_prefix = args.id[0] if args.id else ""
        return super().validate_args(args)

    def run(self, args):
        """Dispatch to show-task or show-habit based on the ID prefix."""
        dispatch = {cls.name: cls for cls in Command.__subclasses__()}
        if args._id_prefix == "t":
            dispatch["show-task"]().run(args)
        elif args._id_prefix == "h":
            dispatch["show-habit"]().run(args)
        else:
            raise ValueError(
                f"Unknown ID type '{args._id_prefix}': "
                "use t... for tasks or h... for habits"
            )
