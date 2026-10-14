"""Read-only ticket search - CampusFlow Next (Engineer B).

Contract
--------
search_tickets(tickets, keyword, category=None, status=None, priority=None)
  * Pure function: never modifies `tickets` or any ticket inside it.
  * Always returns a NEW list (a shallow copy of the matches).
  * keyword matches ticket title OR any note message, case-insensitive
    substring match, after trimming spaces.
  * keyword None / blank -> do not filter by keyword (all tickets returned).
  * category / status / priority are optional extra filters. Every filter
    that is supplied must match (logical AND). None / blank = no filter.
"""

PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _clean(value, name):
    """Trim + casefold a text filter. None/blank -> None (means 'no filter')."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string or None")
    value = value.strip().casefold()
    return value or None


def _matches_keyword(ticket, keyword):
    if keyword in str(ticket.get("title", "")).casefold():
        return True
    for note in ticket.get("notes", []) or []:
        if keyword in str(note.get("message", "")).casefold():
            return True
    return False


def _matches_field(ticket, field, wanted):
    return str(ticket.get(field, "")).strip().casefold() == wanted


def search_tickets(tickets, keyword, category=None, status=None, priority=None):
    """Return a new list of tickets matching keyword and all given filters."""
    keyword = _clean(keyword, "keyword")
    category = _clean(category, "category")
    status = _clean(status, "status")
    priority = _clean(priority, "priority")

    results = []
    for ticket in tickets:
        if keyword is not None and not _matches_keyword(ticket, keyword):
            continue
        if category is not None and not _matches_field(ticket, "category", category):
            continue
        if status is not None and not _matches_field(ticket, "status", status):
            continue
        if priority is not None and not _matches_field(ticket, "priority", priority):
            continue
        results.append(ticket)
    return results


def _numeric_id(ticket):
    """'T10' -> 10 so that T2 sorts before T10 (text sort would be wrong)."""
    digits = "".join(ch for ch in str(ticket.get("id", "")) if ch.isdigit())
    return int(digits) if digits else float("inf")


def sort_results_by_priority(tickets):
    """New list sorted critical > high > medium > low, then numeric ticket ID.

    Separate optional view for search results. It does NOT replace the
    original Open Work Queue in queue.py.
    """
    return sorted(
        tickets,
        key=lambda t: (PRIORITY_RANK.get(t.get("priority"), 99), _numeric_id(t)),
    )
