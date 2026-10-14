# CampusFlow Next - Understanding Check (Engineer B)

This page explains the four rule areas of CampusFlow Next. The same text is
returned by `run_understanding_check()` in `campusflow/understanding_check.py`,
and the interactive six-question quiz tests it (menu option 11).

## 1. Priority rules

Priority is calculated from **urgency** and **affected_users**, checked in this
order (the first rule that matches wins):

1. **critical** - high urgency AND affected_users >= 10
2. **high** - high urgency OR affected_users >= 10
3. **medium** - medium urgency OR affected_users >= 3
4. **low** - everything else

Category (Network, Hardware, Software, Other) does **not** change priority. It
is used for search filters and report counts only. Order matters: a high-urgency
ticket with 10 users is critical, not high.

## 2. Workflow rules

- Allowed: `open -> in_progress -> resolved -> open` (reopen). `in_progress`
  may also go back to `open`.
- An **unassigned** open ticket cannot move to `in_progress`; assign it first.
- A **resolved** ticket cannot go straight to `in_progress`; reopen it first.
- A resolved ticket cannot be reassigned or receive notes until it is reopened.
  Notes already written are kept through resolve and reopen.
- A rejected action raises an error and leaves the ticket exactly as it was.

## 3. Search rules

- Search is **read-only**. It returns a new list and never edits a ticket.
- The keyword is trimmed and matched case-insensitively as a substring against
  the ticket **title and every note message**.
- A blank or `None` keyword means "no keyword filter" and returns all tickets.
- Optional category, status and priority filters combine with **AND**: a ticket
  must match every filter that was supplied. Blank filters are ignored.
- No match returns an empty list. There is no fuzzy spelling correction.
- The separate sorted view orders results critical > high > medium > low, then
  by **numeric** ticket ID (so T2 comes before T10). The original Open Work
  Queue is unchanged.

## 4. Storage safety

- On load, the whole file is parsed and validated **before** it replaces
  anything in memory.
- Corrupt JSON, malformed records and duplicate ticket IDs are rejected with a
  clear error, and the tickets already in memory stay unchanged.
- After a successful reload, new ticket and note IDs continue from the existing
  ones so they cannot collide.

## Reports (for the Head of Campus)

The report shows total tickets, counts by status, priority and category,
assigned vs unassigned, unresolved (open + in_progress), resolved, and the
resolution percentage (resolved / total x 100). An empty dataset shows 0%
instead of dividing by zero. A reopened ticket is counted by its **current**
status, so nothing is counted twice.
