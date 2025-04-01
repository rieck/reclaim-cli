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

The command `create-task` (or short `create`) is used to define a new task at [Reclaim.ai](https:/reclaim.ai) and optionally specify its scheduling preferences. At minimum, it requires a `title`, but you can also provide additional data to help Reclaim.ai plan the task effectively.

```sh
usage: reclaim create-task [options] <title>

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
  -s <datetime>, --snooze-until <datetime>
                                        snooze until (default: None)
```

Most of the provided options are self-explanatory. Due dates can be specified in different formats, such as `2023-11-11` or `April 1, 2023` as well as relative formats like `in 2 weeks`. For priorities, Reclaim uses a discrete scale from `1` (lowest) to `4` (highest). Task duration is specified in minutes and supports common time formats, such as `12min`, `4h30m`, or `4:30`. The minimum and maximum chunk sizes follow the same time format as durations. These define how the task can be broken up when scheduled.

#### Example: Create

```sh
reclaim create-task "Write paper draft" -d "in 4 days" -p 2 -D 4h -m 45m -M 2h
```

This creates a task titled "Write paper draft", due in 4 days, with priority 2, a total duration of 3 hours, and preferred work chunks between 45 minutes and 2 hours.

### Listing tasks

The command `list-tasks` (or short `list`) displays an overview of all tasks currently managed by your Reclaim account. By default, this includes tasks that are in progress, scheduled, or pending scheduling. You can use this command to filter tasks by their status or due date.

```sh
usage: reclaim list-tasks [options]

options:
  -h, --help                       show this help message and exit
  -s <list>, --status <list>       filter by status (default: active)
  -d <datetime>, --due <datetime>  filter by due date (default: None)
  -r, --at-risk                    show only at-risk tasks (default: False)
  -o <field>, --order <field>      order by field (default: due)
```

The supported statuses are "active", "in_progress", "scheduled", "new", "complete", and "archived". The "active" status is a shorthand for "new,scheduled,in_progress". Additionally, you can filter to show only at-risk tasks or order the listing by fields like "due", "left", "progress", "status", or "title".

#### Example: List

```sh
reclaim list-tasks -s scheduled,new -o state
```

This lists all tasks that are "in_progress" or "scheduled", sorted by their remaining time. Each task is identified by a short string ID.

### Deleting a teask

The command `delete-task` (or short `delete`) allows you to permanently remove a task from Reclaim.ai. Since this is a destructive operation and deleted tasks cannot be recovered, it should be used with caution.

```sh
usage: reclaim delete-task [options] <id>

positional arguments:
  <id>        task id to delete

options:
  -h, --help  show this help message and exit
```

The task to be deleted is identified by its short string ID, which can be obtained from the task listing.

#### Example: Delete

```sh
reclaim delete-task 5fte1
```

This permanently removes the specified task from your Reclaim.ai account.
