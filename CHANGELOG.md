# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2026-03-16

### Fixed

- Missing event ID for habits not found in the daily habits lookup

### Changed

- Color palette is brightened automatically on dark terminal backgrounds

## [0.2.2] - 2026-03-16

### Added

- `config` command to generate a `~/.reclaim` template with calendars
- Calendar color mapping for user events via `~/.reclaim` config
- Color highlighting for event type and task state columns
- Short aliases for all commands (shown in per-command `--help`)

## [0.2.1] - 2026-03-07

### Added

- External calendar events shown in `list-events`
- `U` event type code for external user calendar events
- Colored dot column (●) before titles in `list-events` and `list-tasks`
- Planned occurrences shown in `show-habit` command
- Shell completion for task and habit IDs via `argcomplete`

### Changed

- Colored dot column moved to the first column in all listings
- Full-day events filtered out from `list-events`
- Events outside the requested date range filtered from API response
- Removed command aliases
- Removed dead code (`_WEEKDAYS`, unused datetime imports)

## [0.2.0] - 2026-03-07

### Added

- New `list-events` command (alias: `events`) to display calendar events
- Compact event type codes (T=task, H=habit, M=meeting) with priority digit

### Changed

- IDs are now prefixed with type letter (`t`, `h`, `m`) across all views
- IDs are bijectively scrambled so numerically close IDs appear unrelated
- Date parsing now prefers future dates for weekday names (e.g. "Monday")

## [0.1.4] - 2026-01-21

### Added

- Support for adding end editing task notes (Chris Parsons)

### Changed

- Minor improvements to documentation and code base

## [0.1.3] - 2025-05-07

### Addded

- Support for showing an estimated workload

### Changed

- Refactored code for string and parse functions
- Switched to new Reclaim SDK 0.6.4

## [0.1.2] - 2025-05-06

### Added

- Option to list all tasks for `list-tasks` command

### Changed

- Minor improvements to argsparse output

## [0.1.1] - 2025-04-26

### Added

- Initial release of Reclaim CLI
- Basic task management commands (create, list, show, edit, delete)
- Time tracking functionality
- Configuration management
- Command-line interface with help formatting

### Changed

- Fixed issues with double parsing of durations
- Renamed location of patched reclaim-sdk on Github
