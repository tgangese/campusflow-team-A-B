"""Ticket assignment and status workflow."""

from campusflow.tickets import find_ticket


ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"open", "resolved"},
    "resolved": {"open"},
}


def assign_ticket(tickets, ticket_id: str, staff_name: str) -> dict:
    """Assign an existing ticket to a staff member."""

    if not isinstance(staff_name, str):
        raise ValueError("Staff name must be a string")

    staff_name = staff_name.strip()

    if not staff_name:
        raise ValueError("Staff name must not be blank")

    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' not found")

    ticket["assigned_to"] = staff_name

    return ticket


def update_ticket_status(tickets, ticket_id: str, new_status: str) -> dict:
    """Update a ticket's status when the transition is allowed."""

    if not isinstance(new_status, str):
        raise ValueError("Status must be a string")

    new_status = new_status.strip().lower()

    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError(
            f"Invalid status '{new_status}'. "
            f"Allowed statuses: {', '.join(ALLOWED_TRANSITIONS)}"
        )

    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' not found")

    current_status = ticket["status"]

    # Prevent an unassigned ticket from moving to in_progress.
    if new_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError("Cannot start work on an unassigned ticket")

    # Check whether the requested status transition is allowed.
    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(
            f"Cannot change status from '{current_status}' "
            f"to '{new_status}'"
        )

    ticket["status"] = new_status

    return ticket