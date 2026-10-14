"""CLI menu helpers - CampusFlow Next (Engineer B).

Each function takes the in-memory `tickets` list and works with injectable
input_fn / print_fn so tests can drive them without typing. Business rules
live in notes.py, workflow.py, search.py and reports.py; this module only
asks, validates each answer immediately, and shows results.

Every field is checked as soon as it is typed. A bad answer shows a message
and re-asks that same field. Type `cancel` at any prompt to return to the menu.
"""

import os

from campusflow.notes import add_note
from campusflow.reports import generate_report, format_report_text
from campusflow.search import search_tickets, sort_results_by_priority
from campusflow.tickets import create_ticket, find_ticket
from campusflow.understanding_check import run_quiz
from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)
from campusflow.workflow import assign_ticket, update_ticket_status

CANCEL_WORD = "cancel"
CATEGORY_CHOICES = ("network", "hardware", "software", "other")
STATUS_CHOICES = ("open", "in_progress", "resolved")
PRIORITY_CHOICES = ("critical", "high", "medium", "low")


def normalize_ticket_id(raw):
    """' t001 ' -> 'T001'. IDs are stored upper-case; users may type any case."""
    return raw.strip().upper() if isinstance(raw, str) else raw


# --- immediate-validation helpers -----------------------------------------

def ask_until_valid(prompt, validate, input_fn=input, print_fn=print):
    """Ask until `validate(raw)` succeeds; return its result.

    validate raises ValueError with a friendly message on bad input, which is
    shown right away before the same field is asked again. Returns None if the
    user types `cancel`.
    """
    while True:
        raw = input_fn(prompt)
        if isinstance(raw, str) and raw.strip().casefold() == CANCEL_WORD:
            print_fn("Cancelled.")
            return None
        try:
            return validate(raw)
        except ValueError as error:
            print_fn(f"Invalid input: {error} (or type 'cancel')")


def _required_text(label):
    def check(raw):
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"{label} cannot be blank")
        return raw.strip()
    return check


def _existing_ticket_id(tickets, extra_check=None):
    def check(raw):
        ticket_id = normalize_ticket_id(raw)
        if not ticket_id:
            raise ValueError("Ticket ID cannot be blank")
        ticket = find_ticket(tickets, ticket_id)
        if ticket is None:
            raise ValueError(f"Ticket {ticket_id} not found")
        if extra_check:
            extra_check(ticket)
        return ticket_id
    return check


def _note_message(raw):
    if not isinstance(raw, str):
        raise ValueError("Message must be text")
    message = raw.strip()
    if not (5 <= len(message) <= 300):
        raise ValueError("Message must be 5-300 characters after trimming")
    return message


def _whole_positive_number(raw):
    try:
        number = int(str(raw).strip())
    except ValueError:
        raise ValueError("Affected users must be a whole number like 5")
    return validate_affected_users(number)


def _status_choice(raw):
    status = str(raw).strip().casefold()
    if status not in STATUS_CHOICES:
        raise ValueError("Status must be open, in_progress or resolved")
    return status


def _note_allowed(ticket):
    if ticket["status"] not in ("open", "in_progress"):
        raise ValueError(f"Cannot add note to resolved ticket {ticket['id']} - reopen first")


def _assign_allowed(ticket):
    if ticket["status"] == "resolved":
        raise ValueError(f"Cannot assign resolved ticket {ticket['id']} - reopen first")


def format_ticket_row(ticket):
    return (
        f"{ticket['id']} | {ticket['title']} | {ticket['category']} | "
        f"{ticket['priority']} | {ticket['status']} | assigned={ticket.get('assigned_to')}"
    )


# --- ticket menus ---------------------------------------------------------

def menu_create_ticket(tickets, input_fn=input, print_fn=print):
    title = ask_until_valid("Title: ", validate_title, input_fn, print_fn)
    if title is None:
        return None
    category = ask_until_valid(
        "Category (Network/Hardware/Software/Other): ", validate_category, input_fn, print_fn)
    if category is None:
        return None
    urgency = ask_until_valid("Urgency (low/medium/high): ", validate_urgency, input_fn, print_fn)
    if urgency is None:
        return None
    affected = ask_until_valid("Affected users: ", _whole_positive_number, input_fn, print_fn)
    if affected is None:
        return None
    try:
        ticket = create_ticket(tickets, title, category, urgency, affected)
    except ValueError as error:
        print_fn(f"Could not create ticket: {error}")
        return None
    print_fn(f"Created {ticket['id']} priority={ticket['priority']}")
    return ticket


def menu_view_ticket(tickets, input_fn=input, print_fn=print):
    ticket_id = ask_until_valid("Ticket ID: ", _existing_ticket_id(tickets), input_fn, print_fn)
    if ticket_id is None:
        return None
    ticket = find_ticket(tickets, ticket_id)
    print_fn(ticket)
    return ticket


def menu_assign_ticket(tickets, input_fn=input, print_fn=print):
    ticket_id = ask_until_valid(
        "Ticket ID: ", _existing_ticket_id(tickets, _assign_allowed), input_fn, print_fn)
    if ticket_id is None:
        return None
    staff = ask_until_valid("Assign to: ", _required_text("Staff name"), input_fn, print_fn)
    if staff is None:
        return None
    try:
        ticket = assign_ticket(tickets, ticket_id, staff)
    except ValueError as error:
        print_fn(f"Could not assign: {error}")
        return None
    print_fn(f"Assigned {ticket_id} to {staff}")
    return ticket


def menu_update_status(tickets, input_fn=input, print_fn=print):
    ticket_id = ask_until_valid("Ticket ID: ", _existing_ticket_id(tickets), input_fn, print_fn)
    if ticket_id is None:
        return None
    status = ask_until_valid(
        "New status (open/in_progress/resolved): ", _status_choice, input_fn, print_fn)
    if status is None:
        return None
    try:
        ticket = update_ticket_status(tickets, ticket_id, status)
    except ValueError as error:
        # e.g. unassigned open ticket -> in_progress, or an illegal transition
        print_fn(f"Could not update status: {error}")
        return None
    print_fn(f"Status updated: {ticket_id} is now {status}")
    return ticket


# --- notes, search, reports, quiz ----------------------------------------

def menu_add_note(tickets, input_fn=input, print_fn=print):
    """Ask for ticket/author/message (each checked immediately), call add_note."""
    ticket_id = ask_until_valid(
        "Ticket ID: ", _existing_ticket_id(tickets, _note_allowed), input_fn, print_fn)
    if ticket_id is None:
        return None
    author = ask_until_valid("Author: ", _required_text("Author"), input_fn, print_fn)
    if author is None:
        return None
    message = ask_until_valid("Note message (5-300 chars): ", _note_message, input_fn, print_fn)
    if message is None:
        return None
    try:
        note = add_note(tickets, ticket_id, author, message)
    except ValueError as error:
        print_fn(f"Could not add note: {error}")
        return None
    print_fn(f"Added {note['note_id']} to {ticket_id}")
    return note


def menu_view_notes(tickets, input_fn=input, print_fn=print):
    """Show every note on a ticket in note-ID order."""
    ticket_id = ask_until_valid("Ticket ID: ", _existing_ticket_id(tickets), input_fn, print_fn)
    if ticket_id is None:
        return []
    ticket = find_ticket(tickets, ticket_id)
    notes = sorted(ticket.get("notes", []), key=lambda n: n["note_id"])
    if not notes:
        print_fn(f"No notes for {ticket_id}")
        return notes
    print_fn(f"--- Notes for {ticket_id} ({ticket['status']}) ---")
    for note in notes:
        print_fn(f"{note['note_id']} | {note['author']} | {note['message']}")
    return notes


def _ask_filter(label, allowed, input_fn, print_fn):
    """Prompt until the user gives blank (no filter) or a valid option."""
    while True:
        raw = input_fn(f"{label} filter ({'/'.join(allowed)}, blank = any): ").strip().casefold()
        if raw == "" or raw in allowed:
            return raw or None
        print_fn(f"Invalid {label.lower()}. Choose one of: {', '.join(allowed)} or leave blank.")


def menu_search(tickets, input_fn=input, print_fn=print):
    """Read-only search: keyword + optional category/status/priority filters.

    Blank is valid here on purpose: blank keyword/filter means "do not filter".
    """
    keyword = input_fn("Search keyword (title or note, blank = all): ")
    category = _ask_filter("Category", CATEGORY_CHOICES, input_fn, print_fn)
    status = _ask_filter("Status", STATUS_CHOICES, input_fn, print_fn)
    priority = _ask_filter("Priority", PRIORITY_CHOICES, input_fn, print_fn)

    results = search_tickets(tickets, keyword, category=category, status=status, priority=priority)
    if not results:
        print_fn("No tickets match your search.")
        return results

    results = sort_results_by_priority(results)
    print_fn(f"--- {len(results)} result(s), sorted by priority then ID ---")
    for ticket in results:
        print_fn(format_ticket_row(ticket))
    return results


def menu_reports(tickets, print_fn=print):
    """Print the full report (safe on an empty ticket list)."""
    report = generate_report(tickets)
    print_fn(format_report_text(report))
    return report


def menu_understanding_check(input_fn=input, print_fn=print, notes_path=None):
    """Run the quiz and optionally save the written explanations."""
    result = run_quiz(input_fn=input_fn, print_fn=print_fn)
    if notes_path:
        os.makedirs(os.path.dirname(notes_path) or ".", exist_ok=True)
        with open(notes_path, "a", encoding="utf-8") as handle:
            handle.write(f"Score: {result['score']}/{result['total']}\n")
            for item in result["explanations"]:
                handle.write(f"{item['question']} ({item['choice']}): {item['explanation']}\n")
            handle.write("\n")
        print_fn(f"Explanations saved to {notes_path}")
    return result
