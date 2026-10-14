from campusflow.tickets import PRIORITY_ORDER

def get_open_tickets(tickets):
    return [t for t in tickets if t["status"] == "open"]

def get_assigned_tickets(tickets, staff_name=None):
    if staff_name:
        key=staff_name.strip().casefold()
        return [t for t in tickets if t.get("assigned_to") and t["assigned_to"].casefold()==key]
    return [t for t in tickets if t.get("assigned_to")]

def sort_by_priority(tickets):
    return sorted(tickets, key=lambda t: PRIORITY_ORDER.get(t["priority"], 99))
