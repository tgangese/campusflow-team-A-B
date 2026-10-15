"""Follow-up notes - CampusFlow"""

from campusflow.tickets import find_ticket

def next_note_id(ticket):
    notes = ticket.get("notes", [])
    if not notes:
        return "N001"
    max_n = max(int(n["note_id"][1:]) for n in notes)
    return f"N{max_n+1:03d}"

def add_note(tickets, ticket_id, author, message):
    # find ticket - case-insensitive via central find_ticket
    ticket = find_ticket(tickets, ticket_id)
    if not ticket:
        raise ValueError(f"Ticket {ticket_id} not found")
    
    # status guard - must check BEFORE consuming ID
    if ticket["status"] not in ("open", "in_progress"):
        raise ValueError(f"Cannot add note to resolved ticket {ticket['id']} - reopen first")
    
    # validate author immediately
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Author cannot be blank")
    author = author.strip()
    
    # validate message 5-300 after trim immediately
    if not isinstance(message, str):
        raise ValueError("Message must be string")
    msg = message.strip()
    if not (5 <= len(msg) <= 300):
        raise ValueError("Message must be 5-300 characters after trimming")
    
    # ONLY NOW generate ID - so failed attempts don't consume N001
    nid = next_note_id(ticket)
    note = {"note_id": nid, "author": author, "message": msg}
    ticket.setdefault("notes", []).append(note)
    return note