import copy
import unittest

from campusflow.search import search_tickets


def make_tickets():
    return [
        {"id": "T001", "title": "WiFi down in Library", "category": "Network",
         "urgency": "high", "affected_users": 12, "priority": "critical",
         "status": "open", "assigned_to": None,
         "notes": [{"note_id": "N001", "author": "Mentor A",
                    "message": "Router reboot attempted"}]},
        {"id": "T002", "title": "Laptop screen flickers", "category": "Hardware",
         "urgency": "low", "affected_users": 1, "priority": "low",
         "status": "open", "assigned_to": "Sam", "notes": []},
        {"id": "T003", "title": "Install Python", "category": "Software",
         "urgency": "medium", "affected_users": 3, "priority": "medium",
         "status": "in_progress", "assigned_to": "Sam", "notes": []},
    ]


class TestSearchTickets(unittest.TestCase):

    def setUp(self):
        self.tickets = make_tickets()

    def test_search_by_title_case_insensitive(self):
        for keyword in ("wifi", "WIFI", "WiFi", "lib"):
            result = search_tickets(self.tickets, keyword)
            self.assertEqual([t["id"] for t in result], ["T001"], keyword)

    def test_search_by_note_message(self):
        result = search_tickets(self.tickets, "ROUTER reboot")
        self.assertEqual([t["id"] for t in result], ["T001"])

    def test_blank_keyword_returns_all(self):
        for keyword in (None, "", "   "):
            result = search_tickets(self.tickets, keyword)
            self.assertEqual(result, self.tickets)
            self.assertIsNot(result, self.tickets)  # a copy, not the original list

    def test_no_match_returns_empty(self):
        self.assertEqual(search_tickets(self.tickets, "printer"), [])

    def test_search_does_not_modify_original(self):
        before = copy.deepcopy(self.tickets)
        search_tickets(self.tickets, "wifi")
        search_tickets(self.tickets, "")
        search_tickets(self.tickets, "zzz", category="Network", status="open")
        self.assertEqual(self.tickets, before)

    def test_search_trims_keyword(self):
        result = search_tickets(self.tickets, "   laptop  ")
        self.assertEqual([t["id"] for t in result], ["T002"])


if __name__ == "__main__":
    unittest.main()
