# Reclaim CLI

This tool provides a simple and flexible command-line interface (CLI) for managing tasks at [Reclaim.ai](https://reclaim.ai). At its core, the tool operates through a set of commands, each targeting a specific aspect of task management. The commands allow you to create tasks, log work, lists tasks, start and stop time tracking, and more.

To see the available commands, you can simply run `reclaim --help`, once the tools has been installed.

```console
reclaim --help
usage: reclaim [options] <command> ...

Reclaim CLI

positional arguments:
    add-time            add time to a task
    create-task         create a task
    delete-task         delete a task
    edit-task           edit a task
    list-events         list calendar events
    list-tasks          list tasks
    log-work            log work to a task
    mark-task           mark a task (in)complete
    show-habit          show a habit
    show-load           show estimated workload
    show-task           show a task
    start-task          start a task
    stop-task           stop a task

options:
  -h, --help            show this help message and exit
  -c, --config <file>   set config file (default: ~/.reclaim)
```

Each command can be extended with its further options. Simply run `reclaim <command> --help` to the see available options for a command. 

## Authentication

To authenticate the tool with Reclaim.ai, you first need to obtain an API token from your account. Visit the [developer settings page](https://app.reclaim.ai/settings/developer) and generate a new API token. Once you have your token, you can provide it to the reclaim CLI in one of two ways

(1) Add the token to the configuration file `~/.reclaim` in your home directory:

```console
$ echo "reclaim_token: <token>" >> ~/.reclaim
```

(2) Set the environment variable `RECLAIM_TOKEN` with your token value:

```console
$ export RECLAIM_TOKEN=<token>
```

This ensures the tool can securely authenticate and interact with your Reclaim.ai account.

## Example

Here is a simple example illustrating how to use the tool. Suppose you want to create a task for writing a new blog post with a duration of 8 hours and a due date in 10 days. You would run:

```sh
reclaim create-task "Write new blog post" --duration 8h --due "in 10 days"
# ✓ Created | Id: t3k9mw | Title: Write new blog post
```

The output of the tool is shown as comment in the example. You can then list your tasks like this:

```sh
reclaim list-tasks
# Id      Due          Left   Prog  State  Title
# t3k9mw  2025-04-13   8h0m    0%   N3     Write new blog post
```

Your task has state `N` (new) with default priority 3. Later, you realize that you need less time for the task. Simply update it using its identifier:

```sh
reclaim edit-task t3k9mw --duration 4h
# ✓ Edited | Id: t3k9mw | Title: Write new blog post
```

You can also view your upcoming calendar events with the `list-events` command:

```sh
reclaim list-events --future 3
# Id      Date        Start    Dur  Type  Title
# t3k9mw  2025-04-10  09:00   1h0m   T3   Write new blog post
# h2plta  2025-04-10  12:30   1h0m   H1   🍕 Lunch
# m3hsaa  2025-04-11  14:00   1h0m   M4   Team Meeting
```

Events are shown with a compact type code: `T` for tasks, `H` for habits, `M` for meetings, each followed by the priority digit. The ID column links events back to their source — task IDs can be passed to commands such as `show-task`, `edit-task`, or `start-task`, and habit IDs to `show-habit`:

```sh
reclaim show-habit h2plta
# Habit h2plta: 🍕 Lunch
#    Status:       enabled        Priority:     P1
#    Duration:     1h0m - 1h0m    Ideal time:   12:30
#    Recurrence:   daily          Category:     personal
#    Created:      2023-04-16     Defense:      high
#    Updated:      2024-04-10     Private:      yes
```

Eventually, you notice that nobody reads blogs anymore, so you delete the task and move on:

```sh
reclaim delete-task t3k9mw
# ✓ Deleted | Id: t3k9mw | Title: Write new blog post
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

## Shell Completion

The tool supports shell completion for commands, options, and — most usefully — task and habit IDs. To enable it, generate a completion script after installation.

**Fish:**

```sh
register-python-argcomplete --shell fish reclaim > ~/.config/fish/completions/reclaim.fish
```

**Bash:**

```sh
echo 'eval "$(register-python-argcomplete reclaim)"' >> ~/.bashrc
```

**Zsh:**

```sh
echo 'eval "$(register-python-argcomplete reclaim)"' >> ~/.zshrc
```

Once activated, pressing `<Tab>` after a command that takes an ID will fetch and complete active task or habit IDs from your account.

## Dependencies

The tool relies on the [unofficial Reclaim.ai Python SDK](https://github.com/labiso-gmbh/reclaim-sdk) developed by Labiso GmbH.
