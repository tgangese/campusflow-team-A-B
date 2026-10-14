import copy
import unittest

from campusflow.cli import menu_add_note, menu_reports, menu_search, menu_view_notes
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, update_ticket_status


def scripted(inputs):
    items = iter(inputs)
    return lambda prompt="": next(items)


class TestCliMenus(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        create_ticket(self.tickets, "Laptop dead", "Hardware", "low", 1)
        self.out = []

    def test_add_note_success_then_view_in_id_order(self):
        menu_add_note(self.tickets, scripted(["T001", "Mentor A", "Router reboot tried"]), self.out.append)
        menu_add_note(self.tickets, scripted(["T001", "Mentor B", "Checking switch ports"]), self.out.append)
        notes = menu_view_notes(self.tickets, scripted(["T001"]), self.out.append)
        self.assertEqual([n["note_id"] for n in notes], ["N001", "N002"])

    def test_add_note_rejection_shows_message_and_changes_nothing(self):
        before = copy.deepcopy(self.tickets)
        for ticket_id, author, message in [("T001", "Mentor", "hi"), ("T001", " ", "long enough note"), ("T999", "M", "long enough note")]:
            result = menu_add_note(self.tickets, scripted([ticket_id, author, message]), self.out.append)
            self.assertIsNone(result)
        self.assertEqual(self.tickets, before)
        self.assertTrue(all("Could not add note" in line for line in self.out))

    def test_add_note_on_resolved_ticket_is_rejected(self):
        assign_ticket(self.tickets, "T001", "Sam")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")
        result = menu_add_note(self.tickets, scripted(["T001", "Mentor", "Trying to add late"]), self.out.append)
        self.assertIsNone(result)
        self.assertEqual(self.tickets[0]["notes"], [])

    def test_search_reprompts_on_invalid_filter(self):
        # invalid category 'food' is rejected, then blank accepted
        inputs = ["wifi", "food", "", "", ""]
        results = menu_search(self.tickets, scripted(inputs), self.out.append)
        self.assertEqual([t["id"] for t in results], ["T001"])
        self.assertTrue(any("Invalid category" in line for line in self.out))

    def test_search_no_results_message_and_no_mutation(self):
        before = copy.deepcopy(self.tickets)
        results = menu_search(self.tickets, scripted(["printer", "", "", ""]), self.out.append)
        self.assertEqual(results, [])
        self.assertIn("No tickets match your search.", self.out)
        self.assertEqual(self.tickets, before)

    def test_reports_menu_on_empty_list_does_not_crash(self):
        report = menu_reports([], self.out.append)
        self.assertEqual(report["resolution_percentage"], 0)
        self.assertIn("Total tickets: 0", self.out[0])


if __name__ == "__main__":
    unittest.main()


class TestTicketIdCase(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        self.out = []

    def test_normalize_ticket_id(self):
        from campusflow.cli import normalize_ticket_id
        self.assertEqual(normalize_ticket_id(" t001 "), "T001")
        self.assertEqual(normalize_ticket_id("T001"), "T001")

    def test_add_and_view_note_accept_lowercase_ticket_id(self):
        note = menu_add_note(self.tickets, scripted(["t001", "Mentor A", "Router reboot tried"]), self.out.append)
        self.assertEqual(note["note_id"], "N001")
        notes = menu_view_notes(self.tickets, scripted([" t001 "]), self.out.append)
        self.assertEqual(len(notes), 1)

    def test_unknown_id_still_rejected_after_normalizing(self):
        self.assertIsNone(menu_add_note(self.tickets, scripted(["t999", "Mentor", "Router reboot tried"]), self.out.append))
        self.assertEqual(self.tickets[0]["notes"], [])
