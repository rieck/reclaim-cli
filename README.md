# Reclaim CLI

This tool provides a simple and flexible command-line interface (CLI) for managing tasks at [Reclaim.ai](https://reclaim.ai). At its core, the tool operates through a set of commands, each targeting a specific aspect of task management. The commands allow you to create tasks, log work, lists tasks, start and stop time tracking, and more.

To see the available commands, you can simply run `reclaim --help`, once the tools has been installed.

```console
reclaim --help
usage: reclaim [options] <command> ...

Reclaim CLI

positional arguments:
    add-time (add)                      add time to a task
    create-task (create)                create a task
    delete-task (delete)                delete a task
    list-tasks (list)                   list tasks
    log-work (log)                      log work to a task
    mark-task (mark)                    mark a task (in)complete
    show-task (show)                    show a task
    start-task (start)                  start a task
    stop-task (stop)                    stop a task

options:
  -h, --help                            show this help message and exit
  -c <file>, --config <file>            set config file (default: ~/.reclaim)
```

Each command can be extended with its further options. Simply run `reclaim <command> --help` to the see available options for a command. For example, the following output shows all options available with the command `create-task`:

```console
$ reclaim create-task --help
usage: reclaim create-task [...] <title>

positional arguments:
  <title>                               title of the task

options:
  -h, --help                            show this help message and exit
  -d <datetime>, --due <datetime>       due date of the task
  -p <priority>, --priority <priority>  priority of the task
  -D <duration>, --duration <duration>  duration of the task
  -m <duration>, --min-chunk-size <duration>
                                        minimum chunk size
  -M <duration>, --max-chunk-size <duration>
                                        maximum chunk size
  -s <datetime>, --snooze-until <datetime>
                                        snooze until
```

## Example

Here is a simple example illustrating how to use the tool. Suppose you want to create a task for writing a new blog post with a duration of 8 hours and a due date in 20 days. You would run:

```sh
reclaim create-task "Write new blog post" --duration 8h -due "in 10 days" 
# ✓ Created | Id: 5g5p4 | Title: Write new blog post
```

The output of the tool is shown as comment in the example. You can then list your tasks like this:

```sh
reclaim list-tasks
# Id     Due          Left  Prog  State  Title                  
# 5g5p4  2025-04-13   8h0m    0%   N3    Write new blog post
```

You task has state `N` (new) with default priority 3. Later, you realize that you need less time for the task. Simply update it using its identifier:

```sh
reclaim edit-task 5g5p4 --duration 4h
# ✓ Edited | Id: 5g5p4 | Title: Write new blog post
```

Eventually, you notice that nobody reads blogs anymore, so you delete the task and move on:

```sh
reclaim delete-task 5g5p4
# ✓ Deleted | Id: 5g5p4 | Title: Write new blog post
```

## Installation

The tool is easiest installed directly via pip

```sh
pip install reclaim-cli
```

This will install the latest version of the tool. You can also install it in development mode by cloning the Github repository and running:

```sh
git clone https://github.com/rieck/reclaim-cli.git
cd reclaim-cli
pip install -e ".[dev]"
```

After installation, the `reclaim` command will be available in your local environment. If you want to work on the tool, you can use the following tools to streamline your implementation.

```sh
pre-commit install
black src/
isort src/
flake8 src/
pytest
```

## Dependencies

The tool relies on the [unofficial Reclaim.ai Python SDK](https://github.com/labiso-gmbh/reclaim-sdk) developed by Labiso GmbH. However, since it requires functionality beyond what is available in version `v0.6.3` of the SDK, the dependency is installed from a [patched fork](https://github.com/rieck/reclaim-sdk/tree/fixed).
