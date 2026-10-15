# CampusFlow Next

A reliable Python command-line helpdesk for campus support staff. Staff register
problems (Wi-Fi, laptops, software installs, learning tools), track them through a
safe workflow, leave structured follow-up notes, search tickets, and read trustworthy
reports. Built with the Python standard library only (functions, dictionaries/lists,
JSON, `unittest`).

## Team

| Role | Name | Owns |
|------|------|------|
| Engineer A - Ticket Safety and Storage | Felix Gangese Terkula ([@tgangese](https://github.com/tgangese)) | Validation helpers, ticket workflow guards, notes data layer, JSON save/load and ID continuity |
| Engineer B - Search, Reporting and CLI | Grace Omale ([@OmaleGrace](https://github.com/OmaleGrace)) | Search, report insights, CLI menus and input validation, Engineering Understanding Check |

## Contributors

- **Felix Gangese Terkula** - Engineer A
- **Grace Omale** - Engineer B

## Features

- Create tickets; priority is calculated from urgency and affected users
- Assign tickets and move them through a guarded status workflow
- Original Open Work Queue: open tickets only, critical > high > medium > low, then by ticket ID
- Structured follow-up notes (author + 5-300 character message, per-ticket IDs `N001`, `N002`, ...)
- Read-only search over ticket titles and note messages, with optional category, status and priority filters
- Reports: totals, counts by status/priority/category, assigned vs unassigned, unresolved, resolved, resolution percentage
- Safe JSON storage that validates the whole file before it replaces memory
- Interactive "Engineering Understanding Check" quiz (6 questions)

## Quick start (fresh clone)

```
git clone https://github.com/tgangese/campusflow-team-A-B.git
cd campusflow-team-A-B
python3 -m unittest discover -s tests -v
python3 main.py
```

Requires Python 3 and nothing else. Run `main.py` from the project folder; tickets are
saved to `data/tickets.json` (created on first save). **Choose option 12 (Save & Exit)
to save** - closing the window or pressing Ctrl+C does not save.

## Menu

| # | Option |
|---|--------|
| 1 | Create ticket |
| 2 | List tickets |
| 3 | View ticket |
| 4 | Assign ticket |
| 5 | Update status |
| 6 | Show priority queue (original Open Work Queue) |
| 7 | Add follow-up note |
| 8 | Search tickets |
| 9 | Reports |
| 10 | View ticket notes |
| 11 | Engineering Understanding Check |
| 12 | Exit |

Every field is validated as soon as you press Enter and only that field is asked again.
Type `cancel` at any prompt to go back to the menu without changing anything.
Ticket IDs are accepted in any letter case (`t001` = `T001`).

## Rules

**Priority** (checked in this order, first match wins):

1. critical - high urgency AND affected_users >= 10
2. high - high urgency OR affected_users >= 10
3. medium - medium urgency OR affected_users >= 4
4. low - everything else

Category does not affect priority.

**Status workflow:** `open -> in_progress -> resolved -> open` (reopen); `in_progress` may
also return to `open`. An unassigned open ticket cannot move to `in_progress`. A resolved
ticket cannot be reassigned or receive notes until it is reopened. A rejected action
leaves the data unchanged.

**Validation:** category is Network, Hardware, Software or Other; urgency is low, medium
or high; title cannot be blank; `affected_users` must be a strictly positive integer
(floats, strings and booleans are rejected); assignment needs a non-blank staff label.

**Notes:** only open or in-progress tickets accept notes. A rejected note does not use
up a note ID. Notes are kept through resolve and reopen.

**Search:** read-only. The keyword is trimmed and matched case-insensitively as a
substring of the title or any note message; blank means no keyword filter. Category,
status and priority filters combine with AND. A separate sorted view orders results by
priority, then numeric ticket ID.

**Reports:** reopened tickets count by their current status, so nothing is counted
twice. An empty dataset reports 0% instead of dividing by zero.

## Data format

`data/tickets.json` is a JSON list of ticket objects:

```json
[
  {
    "id": "T001",
    "title": "WiFi down in Library",
    "category": "Network",
    "urgency": "high",
    "affected_users": 12,
    "priority": "critical",
    "status": "in_progress",
    "assigned_to": "Sam",
    "notes": [
      {"note_id": "N001", "author": "Mentor A", "message": "Router reboot attempted"}
    ]
  }
]
```

On load, the whole file is parsed and validated before it replaces anything in memory.
Corrupt JSON, a non-list root, missing keys, bad note shapes, and duplicate ticket or
note IDs are rejected with a clear message, and current data is left untouched.

## Running the tests

```
python3 -m unittest discover -s tests -v
```

All tests must pass from a fresh clone.

## Git workflow

- Feature branches: `feat/21-validation-and-notes` (Engineer A) and `feat/22-search-and-insights` (Engineer B)
- No direct feature commits to `main`; each change goes through a pull request that the other engineer reviews and approves before merge
- After each merge, the integrated test suite is run again on `main`

## AI assistance

AI tools were used as learning and building support on this project. The first version of
the Engineer B search, reports, CLI and quiz code was generated with Claude (Anthropic)
and then reviewed, run and extended by the team. Our verification steps and the
decisions we made are recorded in `docs/ai-learning-log.md`.

## Known issues

- `campusflow/tickets.py` currently uses `affected_users >= 4` for medium priority, but
  the rule above is `>= 3`. Under review; remove this note once fixed.
