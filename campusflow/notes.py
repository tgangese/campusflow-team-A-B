def next_note_id(ticket):
    notes = ticket.get("notes", [])
    if not notes:
        return "N001"
    max_n = max(int(n["note_id"][1:]) for n in notes)
    return f"N{max_n+1:03d}"

def add_note(tickets, ticket_id, author, message):
    # find ticket
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        raise ValueError(f"Ticket {ticket_id} not found")
    
    # status guard
    if ticket["status"] not in ("open", "in_progress"):
        raise ValueError("Cannot add note to resolved ticket - reopen first")
    
    # validate author
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Author cannot be blank")
    author = author.strip()
    
    # validate message 5-300 after trim
    if not isinstance(message, str):
        raise ValueError("Message must be string")
    msg = message.strip()
    if not (5 <= len(msg) <= 300):
        raise ValueError("Message must be 5-300 characters after trimming")
    
    # ONLY NOW generate ID
    nid = next_note_id(ticket)
    note = {"note_id": nid, "author": author, "message": msg}
    ticket["notes"].append(note)
    return note
