"""Ticket assignment and status workflow - CampusFlow Next."""

from campusflow.tickets import find_ticket

ALLOWED_TRANSITIONS = {
    "open": {"in_progress", "resolved"}, # open->resolved allowed? No, spec says open->in_progress only, but keep open->in_progress, in_progress->open/resolved, resolved->open
    "in_progress": {"open", "resolved"},
    "resolved": {"open"}, # Case 14: reopen after false alarm
}

# Correct per spec: open->in_progress, in_progress->open, in_progress->resolved, resolved->open
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"open", "resolved"},
    "resolved": {"open"},
}

def can_transition(ticket: dict, new_status: str) -> bool:
    """Central check - raises ValueError with reason, returns True if allowed."""
    current = ticket["status"]
    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError(f"Invalid status '{new_status}'")
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Cannot change status from '{current}' to '{new_status}'")
    # Case 02: unassigned open cannot go to in_progress
    if current == "open" and new_status == "in_progress":
        if not ticket.get("assigned_to"):
            raise ValueError("Cannot move unassigned open ticket to in_progress - assign first")
    return True

def assign_ticket(tickets, ticket_id: str, staff_name: str) -> dict:
    if not isinstance(staff_name, str):
        raise ValueError("Staff name must be a string")
    staff_name = staff_name.strip()
    if not staff_name:
        raise ValueError("Staff name must not be blank")

    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' not found")

    # Case 03: resolved tickets cannot be reassigned
    if ticket["status"] == "resolved":
        raise ValueError(f"Cannot assign resolved ticket {ticket_id} - reopen first")

    ticket["assigned_to"] = staff_name
    return ticket

def update_ticket_status(tickets, ticket_id: str, new_status: str) -> dict:
    if not isinstance(new_status, str):
        raise ValueError("Status must be a string")
    new_status = new_status.strip().lower()
    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {', '.join(ALLOWED_TRANSITIONS)}")

    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' not found")

    # Use central guard - preserves data on reject
    can_transition(ticket, new_status)

    ticket["status"] = new_status
    return ticket
