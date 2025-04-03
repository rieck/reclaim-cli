"""Load and initialize the commands.

Copyright (c) 2025 Konrad Rieck <konrad@mlsec.org>
"""

import glob
import os

from .base import Command


def load():
    """Find all files in the command directory and import them."""
    cmd_dir = os.path.relpath(os.path.dirname(__file__))

    # get cmd files
    cmd_files = [
        filename
        for filename in glob.glob("%s/*.py" % cmd_dir)
        if not filename.endswith("__init__.py")
    ]

    # import all cmds (except base cmd)
    for cmd_file in cmd_files:
        module_name = os.path.splitext(cmd_file)[0]
        module_name = module_name[module_name.find("reclaim/commands") :]
        module_name = module_name.replace("/", ".")
        if not module_name.endswith("base"):
            __import__(module_name)

    cmds = Command.__subclasses__()
    cmds = [c() for c in cmds]  # Initialize the commands
    return sorted(cmds, key=lambda x: x.name)
