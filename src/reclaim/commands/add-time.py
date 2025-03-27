from .base import Command
from ..utils import get_task, str_to_id, print_done, parse_duration, str_duration


class AddTimeCommand(Command):
    """Add time to task at Reclaim.ai"""

    name = "add-time"
    description = "add time to a task"
    aliases = ["add"]

    def parse_args(self, subparsers):
        """Add arguments to the subparser."""
        subparser = super().parse_args(subparsers)

        subparser.add_argument(
            "id", type=str, metavar="<id>",
            help="task id to add time to"
        )
        subparser.add_argument(
            "duration", type=str, metavar="<duration>",
            help="duration to add"
        )

        return subparser

    def validate_args(self, args):
        """Check and convert command line arguments."""
        try:
            args.id = str_to_id(args.id)
        except ValueError as e:
            raise ValueError(f"Invalid task ID: {str(e)}")
        return args

    def run(self, args):
        """Add time to task at Reclaim.ai"""
        task = get_task(args.id)
        
        # Add time to task
        mins = parse_duration(args.duration)
        task.add_time(mins / 60) # Expects hours
        dur = str_duration(mins, align=False)
        print_done(f"Added: {dur}", task)
