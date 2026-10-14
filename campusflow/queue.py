from campusflow.tickets import PRIORITY_ORDER

def get_open_tickets(tickets):
    return [t for t in tickets if t["status"] == "open"]

def get_assigned_tickets(tickets, staff_name=None):
    # For old test compatibility: blank staff name should raise
    if staff_name is not None:
        if not isinstance(staff_name, str) or not staff_name.strip():
            raise ValueError("Staff name must not be blank")
        key=staff_name.strip().casefold()
        return [t for t in tickets if t.get("assigned_to") and t["assigned_to"].casefold()==key]
    return [t for t in tickets if t.get("assigned_to")]

def sort_by_priority(tickets):
    return sorted(tickets, key=lambda t: PRIORITY_ORDER.get(t["priority"], 99))

def sort_tickets_by_priority(tickets):
    return sort_by_priority(tickets)
