import json
import os
REQUIRED_KEYS = {"id","title","category","urgency","affected_users","priority","status","assigned_to","notes"}

def _validate_ticket_shape(t):
    if not isinstance(t, dict): raise ValueError("Ticket must be dict")
    if not REQUIRED_KEYS.issubset(t.keys()): raise ValueError(f"Missing keys in {t.get('id')}")
    if not isinstance(t["notes"], list): raise ValueError("Notes must be list")
    seen_n=set()
    for n in t["notes"]:
        if not isinstance(n, dict): raise ValueError("Note must be dict")
        if not {"note_id","author","message"}.issubset(n.keys()): raise ValueError("Invalid note shape")
        if n["note_id"] in seen_n: raise ValueError(f"Duplicate note ID {n['note_id']} in ticket {t['id']}")
        seen_n.add(n["note_id"])

def load_tickets(path):
    if not os.path.exists(path):
        return []
    with open(path,'r') as f:
        try: data=json.load(f)
        except json.JSONDecodeError as e: raise ValueError(f"Corrupt JSON: {e}")
    if not isinstance(data,list): raise ValueError("JSON root must be list")
    seen=set()
    for ticket in data:
        _validate_ticket_shape(ticket)
        if ticket["id"] in seen: raise ValueError(f"Duplicate ticket ID {ticket['id']}")
        seen.add(ticket["id"])
    return data

def save_tickets(path,tickets):
    with open(path,'w') as f: json.dump(tickets,f,indent=2)
