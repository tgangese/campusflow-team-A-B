"""Reporting functions for CampusFlow tickets."""


def get_ticket_summary(tickets):
    """Return the total number of tickets."""
    return {
        "total": len(tickets),
    }


def count_tickets_by_status(tickets):
    """Count tickets grouped by status."""
    counts = {}

    for ticket in tickets:
        status = ticket.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1

    return counts


def count_tickets_by_priority(tickets):
    """Count tickets grouped by priority."""
    counts = {}

    for ticket in tickets:
        priority = ticket.get("priority", "unknown")
        counts[priority] = counts.get(priority, 0) + 1

    return counts


def count_tickets_by_category(tickets):
    """Count tickets grouped by category."""
    counts = {}

    for ticket in tickets:
        category = ticket.get("category", "unknown")
        counts[category] = counts.get(category, 0) + 1

    return counts


def count_assignment_status(tickets):
    """Count assigned and unassigned tickets."""
    assigned = sum(
        1
        for ticket in tickets
        if isinstance(ticket.get("assigned_to"), str)
        and ticket["assigned_to"].strip()
    )

    return {
        "assigned": assigned,
        "unassigned": len(tickets) - assigned,
    }


# ---------------------------------------------------------------------------
# CampusFlow Next - Engineer B additions (append-only)
# ---------------------------------------------------------------------------

def count_by_status(tickets):
    """Counts per status. Always includes open/in_progress/resolved keys."""
    counts = {"open": 0, "in_progress": 0, "resolved": 0}
    for ticket in tickets:
        status = ticket.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def count_by_category(tickets):
    """Counts per category. Always includes the four legal categories."""
    counts = {"Network": 0, "Hardware": 0, "Software": 0, "Other": 0}
    for ticket in tickets:
        category = ticket.get("category", "unknown")
        # tolerate old lower-case data without double counting
        for known in counts:
            if isinstance(category, str) and category.strip().casefold() == known.casefold():
                category = known
                break
        counts[category] = counts.get(category, 0) + 1
    return counts


def count_by_priority(tickets):
    """Counts per priority. Always includes critical/high/medium/low."""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for ticket in tickets:
        priority = ticket.get("priority", "unknown")
        counts[priority] = counts.get(priority, 0) + 1
    return counts


def count_assigned_and_unassigned(tickets):
    """Return {"assigned": int, "unassigned": int}. Blank labels are unassigned."""
    assigned = sum(
        1
        for ticket in tickets
        if isinstance(ticket.get("assigned_to"), str)
        and ticket["assigned_to"].strip()
    )
    return {"assigned": assigned, "unassigned": len(tickets) - assigned}


def generate_report(tickets):
    """Build the full report dict. Pure: does not modify tickets.

    Reopened tickets count by their CURRENT status, and every ticket has
    exactly one status, so nothing is double counted.
    resolution_percentage is 0.0 for an empty dataset (no division by zero).
    """
    total = len(tickets)
    by_status = count_by_status(tickets)
    resolved = by_status.get("resolved", 0)
    unresolved = by_status.get("open", 0) + by_status.get("in_progress", 0)
    percentage = round(resolved / total * 100, 1) if total else 0.0
    return {
        "total": total,
        "by_status": by_status,
        "by_priority": count_by_priority(tickets),
        "by_category": count_by_category(tickets),
        "assignment": count_assigned_and_unassigned(tickets),
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": percentage,
    }


def format_report_text(report):
    """Turn a generate_report() dict into printable text."""
    lines = [
        "=== CAMPUSFLOW REPORT ===",
        f"Total tickets: {report['total']}",
        f"Unresolved (open + in_progress): {report['unresolved']}",
        f"Resolved: {report['resolved']}",
        f"Resolution rate: {report['resolution_percentage']}%",
        "",
        "By status:",
    ]
    lines += [f"  {k}: {v}" for k, v in report["by_status"].items()]
    lines.append("By priority:")
    lines += [f"  {k}: {v}" for k, v in report["by_priority"].items()]
    lines.append("By category:")
    lines += [f"  {k}: {v}" for k, v in report["by_category"].items()]
    lines.append("Assignment:")
    lines.append(f"  assigned: {report['assignment']['assigned']}")
    lines.append(f"  unassigned: {report['assignment']['unassigned']}")
    return "\n".join(lines)
