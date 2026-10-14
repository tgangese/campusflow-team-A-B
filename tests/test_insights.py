import unittest

from campusflow.reports import (
    count_assigned_and_unassigned,
    count_by_category,
    count_by_priority,
    count_by_status,
    format_report_text,
    generate_report,
)
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, update_ticket_status


class TestReportInsights(unittest.TestCase):

    def test_empty_report_returns_zero_percent_without_crash(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["resolution_percentage"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertIn("0.0%", format_report_text(report))

    def test_report_counts_after_resolve_and_reopen(self):
        tickets = []
        create_ticket(tickets, "WiFi down", "Network", "high", 12)    # T001
        create_ticket(tickets, "Laptop dead", "Hardware", "low", 1)   # T002
        create_ticket(tickets, "Install app", "Software", "medium", 2)  # T003
        create_ticket(tickets, "Misc", "Other", "low", 1)             # T004
        for tid in ("T001", "T002", "T003"):
            assign_ticket(tickets, tid, "Sam")
            update_ticket_status(tickets, tid, "in_progress")
        update_ticket_status(tickets, "T001", "resolved")
        update_ticket_status(tickets, "T002", "resolved")
        update_ticket_status(tickets, "T002", "open")  # reopened: counts as open NOW

        report = generate_report(tickets)
        self.assertEqual(report["total"], 4)
        self.assertEqual(report["by_status"], {"open": 2, "in_progress": 1, "resolved": 1})
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["unresolved"], 3)  # open + in_progress
        self.assertEqual(report["resolution_percentage"], 25.0)
        self.assertEqual(report["assignment"], {"assigned": 3, "unassigned": 1})
        # nothing double counted: each breakdown adds back up to total
        for key in ("by_status", "by_priority", "by_category"):
            self.assertEqual(sum(report[key].values()), report["total"], key)

    def test_in_progress_counts_as_unresolved(self):
        tickets = [{"status": "in_progress"}, {"status": "resolved"}]
        report = generate_report(tickets)
        self.assertEqual(report["unresolved"], 1)
        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_individual_counters_include_zero_buckets(self):
        self.assertEqual(count_by_status([]), {"open": 0, "in_progress": 0, "resolved": 0})
        self.assertEqual(count_by_priority([])["critical"], 0)
        self.assertEqual(count_by_category([])["Network"], 0)
        self.assertEqual(count_assigned_and_unassigned([]), {"assigned": 0, "unassigned": 0})

    def test_blank_assignment_label_is_unassigned(self):
        tickets = [{"assigned_to": "  "}, {"assigned_to": None}, {"assigned_to": "Sam"}]
        self.assertEqual(count_assigned_and_unassigned(tickets), {"assigned": 1, "unassigned": 2})

    def test_report_does_not_modify_tickets(self):
        tickets = [{"status": "open", "priority": "low", "category": "Other", "assigned_to": None}]
        snapshot = [dict(t) for t in tickets]
        generate_report(tickets)
        self.assertEqual(tickets, snapshot)


if __name__ == "__main__":
    unittest.main()
