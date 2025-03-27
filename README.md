# Reclaim CLI

Copyright (c) 2025 Konrad Rieck (<konrad@mlsec.org>)

## About

This is a simple Python CLI for the Reclaim service.

## Usage

The `reclaim` tool provides a simple and flexible command-line interface (CLI) for managing tasks at [Reclaim.ai](https://reclaim.ai). At its core, `reclaim` operates through a set of commands, each targeting a specific aspect of task management. The commands allow you to create tasks, log work, lists tasks, start and stop time tracking, and more.

To see the available commands, you can run:

```sh
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

Each command follows a consistent pattern and can be extended with its own options, which are described in detail in the sections below.

### Creating a task

The `create-task` command is used to define a new task at [Reclaim.ai](https:/reclaim.ai) and optionally specify its scheduling preferences. At minimum, it requires a `title`, but you can also provide additional data to help Reclaim.ai plan the task effectively.

```sh
reclaim create-task <title> [options]
positional arguments:
  <title>                               title of the task

options:
  -h, --help                            show this help message and exit
  -d <datetime>, --due <datetime>       due date of the task (default: None)
  -p <priority>, --priority <priority>  priority of the task (default: None)
  -D <duration>, --duration <duration>  duration of the task (default: None)
  -m <duration>, --min-chunk-size <duration>
                                        minimum chunk size (default: None)
  -M <duration>, --max-chunk-size <duration>
                                        maximum chunk size (default: None)
```
Most of the provided options are self-explanatory. 

- Due dates (`--due`) can be specified in different formats, such as `2023-11-11 12:12` or `1. April 2023` as well as relative formats like `in 2 weeks` or `next Friday`.

- For priorities (`-priority`), Reclaim uses a discrete scale from `1` (lowest) to `4` (highest).
  
- Task duration (`--duration`) is specified in minutes and supports common time formats, such as `12 minutes`, `4hrs 30min`, or `4:30`.

- The minimum and maximum chunk sizes follow the same time format as durations. These define how the task can be broken up when scheduled.

#### Example

```sh
reclaim create-task "Write paper draft" -d Friday -p 2 -D 3h -m 30m -M 1h
```
This creates a task titled "Write paper draft", due by Friday, with priority 2 , a total duration of 3 hours, and preferred work chunks between 30 minutes and 1 hour.
