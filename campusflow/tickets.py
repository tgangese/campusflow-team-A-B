"""Ticket creation and priority engine."""

def _compute_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 4:
        return "medium"
    return "low"

def create_ticket(tickets, title, category, urgency, affected_users):
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title cannot be blank")
    title = title.strip()
    if not isinstance(category, str):
        raise ValueError("Invalid category")
    canon_cat = {"network": "Network", "hardware": "Hardware", "software": "Software", "other": "Other"}
    key = category.strip().casefold()
    if key not in canon_cat:
        raise ValueError("Category must be Network, Hardware, Software or Other")
    category = canon_cat[key]
    if not isinstance(urgency, str):
        raise ValueError("Invalid urgency")
    ukey = urgency.strip().casefold()
    if ukey not in ("low","medium","high"):
        raise ValueError("Urgency must be low, medium or high")
    urgency = ukey
    if isinstance(affected_users, bool):
        raise ValueError("affected_users cannot be bool")
    if isinstance(affected_users, str):
        raise ValueError("affected_users must be integer")
    if isinstance(affected_users, float):
        raise ValueError("affected_users must be integer, not float")
    if not isinstance(affected_users, int):
        raise ValueError("affected_users must be integer")
    if affected_users <= 0:
        raise ValueError("affected_users must be positive")

    priority = _compute_priority(urgency, affected_users)
    new_id = f"T{len(tickets)+1:03d}"
    ticket = {
        "id": new_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": []
    }
    tickets.append(ticket)
    return ticket

def find_ticket(tickets, ticket_id):
    """Case-insensitive: t001 = T001, ' t001 ' -> T001"""
    if not isinstance(ticket_id, str):
        return None
    tid = ticket_id.strip().upper()
    if not tid:
        return None
    for t in tickets:
        if t.get("id", "").strip().upper() == tid:
            return t
    return None

# --- Compatibility aliases for old tests ---
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
def calculate_priority(urgency, affected_users):
    return _compute_priority(urgency, affected_users)

def validate_affected_users(raw):
    if isinstance(raw, bool): raise ValueError("affected_users cannot be bool")
    if isinstance(raw, str): raise ValueError("affected_users must be integer")
    if isinstance(raw, float): raise ValueError("affected_users must be integer, not float")
    if not isinstance(raw, int): raise ValueError("affected_users must be integer")
    if raw <= 0: raise ValueError("affected_users must be positive")
    return raw