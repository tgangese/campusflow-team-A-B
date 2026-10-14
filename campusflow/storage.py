import json
import os

REQUIRED_KEYS = {"id","title","category","urgency","affected_users","priority","status","assigned_to","notes"}

def _validate_ticket_shape(t):
    if not isinstance(t, dict): raise ValueError("Ticket must be dict")
    if not REQUIRED_KEYS.issubset(t.keys()): raise ValueError(f"Missing keys in {t.get('id')}")
    # validate notes shape
    if not isinstance(t["notes"], list): raise ValueError("Notes must be list")
    seen_n = set()
    for n in t["notes"]:
        if not isinstance(n, dict): raise ValueError("Note must be dict")
        if not {"note_id","author","message"}.issubset(n.keys()): raise ValueError("Invalid note shape")
        if n["note_id"] in seen_n: raise ValueError(f"Duplicate note ID {n['note_id']} in ticket {t['id']}")
        seen_n.add(n["note_id"])
        if not (5 <= len(n["message"].strip()) <= 300): raise ValueError("Invalid stored note length")

def load_tickets(path):
    # Parse and validate BEFORE replacing memory
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupt JSON: {e}")
    
    if not isinstance(data, list):
        raise ValueError("JSON root must be list")
    
    seen_ids = set()
    for ticket in data:
        _validate_ticket_shape(ticket)
        tid = ticket["id"]
        if tid in seen_ids:
            raise ValueError(f"Duplicate ticket ID {tid}")
        seen_ids.add(tid)
        # basic field validation
        if ticket["category"] not in ("Network","Hardware","Software","Other"):
            raise ValueError(f"Invalid category in {tid}")
        if ticket["urgency"] not in ("low","medium","high"):
            raise ValueError(f"Invalid urgency in {tid}")
        if ticket["status"] not in ("open","in_progress","resolved"):
            raise ValueError(f"Invalid status in {tid}")
    
    return data

def save_tickets(path, tickets):
    with open(path, 'w') as f:
        json.dump(tickets, f, indent=2)
