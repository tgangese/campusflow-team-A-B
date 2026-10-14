"""CLI menu helpers - CampusFlow Next (Engineer B).

Each function takes the in-memory `tickets` list and works with injectable
input_fn / print_fn so tests can drive them without typing. Business rules
live in notes.py, search.py and reports.py; this module only asks and shows.
"""

import os

from campusflow.notes import add_note
from campusflow.reports import generate_report, format_report_text
from campusflow.search import search_tickets, sort_results_by_priority
from campusflow.tickets import find_ticket
from campusflow.understanding_check import run_quiz

CATEGORY_CHOICES = ("network", "hardware", "software", "other")
STATUS_CHOICES = ("open", "in_progress", "resolved")
PRIORITY_CHOICES = ("critical", "high", "medium", "low")


def _ask_filter(label, allowed, input_fn, print_fn):
    """Prompt until the user gives blank (no filter) or a valid option."""
    while True:
        raw = input_fn(f"{label} filter ({'/'.join(allowed)}, blank = any): ").strip().casefold()
        if raw == "" or raw in allowed:
            return raw or None
        print_fn(f"Invalid {label.lower()}. Choose one of: {', '.join(allowed)} or leave blank.")


def format_ticket_row(ticket):
    return (
        f"{ticket['id']} | {ticket['title']} | {ticket['category']} | "
        f"{ticket['priority']} | {ticket['status']} | assigned={ticket.get('assigned_to')}"
    )


def menu_add_note(tickets, input_fn=input, print_fn=print):
    """Ask for ticket/author/message, call add_note, show friendly feedback."""
    ticket_id = input_fn("Ticket ID: ").strip()
    author = input_fn("Author: ")
    message = input_fn("Note message (5-300 chars): ")
    try:
        note = add_note(tickets, ticket_id, author, message)
    except ValueError as error:
        print_fn(f"Could not add note: {error}")
        return None
    print_fn(f"Added {note['note_id']} to {ticket_id}")
    return note


def menu_view_notes(tickets, input_fn=input, print_fn=print):
    """Show every note on a ticket in note-ID order."""
    ticket_id = input_fn("Ticket ID: ").strip()
    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        print_fn(f"Ticket {ticket_id} not found")
        return []
    notes = sorted(ticket.get("notes", []), key=lambda n: n["note_id"])
    if not notes:
        print_fn(f"No notes for {ticket_id}")
        return notes
    print_fn(f"--- Notes for {ticket_id} ({ticket['status']}) ---")
    for note in notes:
        print_fn(f"{note['note_id']} | {note['author']} | {note['message']}")
    return notes


def menu_search(tickets, input_fn=input, print_fn=print):
    """Read-only search: keyword + optional category/status/priority filters."""
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
