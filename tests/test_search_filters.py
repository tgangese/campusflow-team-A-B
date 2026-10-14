import copy
import unittest

from campusflow.search import search_tickets, sort_results_by_priority
from tests.test_search import make_tickets


class TestCombinedFilters(unittest.TestCase):

    def setUp(self):
        self.tickets = make_tickets()
        self.tickets.append(
            {"id": "T004", "title": "WiFi slow in Lab", "category": "Network",
             "urgency": "low", "affected_users": 2, "priority": "low",
             "status": "resolved", "assigned_to": "Sam", "notes": []}
        )

    def ids(self, result):
        return [t["id"] for t in result]

    def test_combined_filters_use_and(self):
        result = search_tickets(self.tickets, "wifi", category="Network", status="open")
        self.assertEqual(self.ids(result), ["T001"])

    def test_one_failing_filter_excludes_ticket(self):
        # title matches T001 but category does not -> AND means no result
        self.assertEqual(search_tickets(self.tickets, "wifi", category="Hardware"), [])

    def test_empty_filters_mean_no_filter(self):
        result = search_tickets(self.tickets, "wifi", category="", status=None, priority="  ")
        self.assertEqual(self.ids(result), ["T001", "T004"])

    def test_filters_are_case_insensitive(self):
        result = search_tickets(self.tickets, "", category="NETWORK", priority="Low")
        self.assertEqual(self.ids(result), ["T004"])

    def test_filtered_search_does_not_modify_original(self):
        before = copy.deepcopy(self.tickets)
        search_tickets(self.tickets, "wifi", category="Network", status="open", priority="critical")
        self.assertEqual(self.tickets, before)


class TestSortResults(unittest.TestCase):

    def test_sorts_by_priority_then_numeric_id(self):
        tickets = [
            {"id": "T10", "priority": "high"},
            {"id": "T2", "priority": "high"},
            {"id": "T3", "priority": "critical"},
            {"id": "T1", "priority": "low"},
        ]
        result = sort_results_by_priority(tickets)
        # text sort would put 'T10' before 'T2'; numeric tie-break must not
        self.assertEqual([t["id"] for t in result], ["T3", "T2", "T10", "T1"])

    def test_sort_returns_new_list_and_keeps_original_order(self):
        tickets = [{"id": "T2", "priority": "low"}, {"id": "T1", "priority": "high"}]
        result = sort_results_by_priority(tickets)
        self.assertEqual([t["id"] for t in tickets], ["T2", "T1"])
        self.assertIsNot(result, tickets)


if __name__ == "__main__":
    unittest.main()
