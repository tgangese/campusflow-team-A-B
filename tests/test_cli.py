import copy
import unittest

from campusflow.cli import (
    menu_add_note,
    menu_assign_ticket,
    menu_create_ticket,
    menu_reports,
    menu_search,
    menu_update_status,
    menu_view_notes,
    menu_view_ticket,
)
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

    def test_each_note_field_is_rejected_immediately_then_reasked(self):
        # blank author and too-short message are caught at THEIR field,
        # and the rejected attempts must not consume a note ID.
        inputs = ["T001", "   ", "Mentor", "hi", "Router reboot tried"]
        note = menu_add_note(self.tickets, scripted(inputs), self.out.append)
        self.assertEqual(note["note_id"], "N001")
        self.assertTrue(any("Author cannot be blank" in line for line in self.out))
        self.assertTrue(any("5-300 characters" in line for line in self.out))
        self.assertEqual(len(self.tickets[0]["notes"]), 1)

    def test_cancel_leaves_collection_unchanged(self):
        before = copy.deepcopy(self.tickets)
        for inputs in (["cancel"], ["T001", "cancel"], ["T001", "Mentor", "CANCEL"], ["T999", "cancel"]):
            self.out.clear()
            self.assertIsNone(menu_add_note(self.tickets, scripted(inputs), self.out.append))
            self.assertIn("Cancelled.", self.out)
        self.assertEqual(self.tickets, before)
    def test_add_note_on_resolved_ticket_is_rejected_at_the_ticket_id_field(self):
        assign_ticket(self.tickets, "T001", "Sam")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")
        result = menu_add_note(self.tickets, scripted(["T001", "cancel"]), self.out.append)
        self.assertIsNone(result)
        self.assertTrue(any("reopen first" in line for line in self.out))
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

    def test_unknown_id_rejected_after_normalizing(self):
        out = []
        result = menu_add_note(self.tickets, scripted(["t999", "cancel"]), out.append)
        self.assertIsNone(result)
        self.assertTrue(any("T999 not found" in line for line in out))
        self.assertEqual(self.tickets[0]["notes"], [])


class TestImmediateFieldValidation(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        self.out = []

    def test_create_ticket_rejects_each_bad_field_immediately(self):
        inputs = [
            "", "   ", "WiFi down",          # title: blank twice, then valid
            "", "food", "network",           # category
            "", "urgent", "HIGH",            # urgency
            "", "abc", "2.5", "0", "-3", "12",  # affected users
        ]
        ticket = menu_create_ticket(self.tickets, scripted(inputs), self.out.append)
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 12)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(len(self.tickets), 1)
        self.assertEqual(sum("Invalid input" in line for line in self.out), 11)

    def test_create_ticket_cancel_adds_nothing(self):
        self.assertIsNone(menu_create_ticket(self.tickets, scripted(["WiFi", "cancel"]), self.out.append))
        self.assertEqual(self.tickets, [])

    def test_assign_rejects_blank_id_and_blank_staff_immediately(self):
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        ticket = menu_assign_ticket(self.tickets, scripted(["", "t001", "  ", "Sam"]), self.out.append)
        self.assertEqual(ticket["assigned_to"], "Sam")
        self.assertTrue(any("Ticket ID cannot be blank" in line for line in self.out))
        self.assertTrue(any("Staff name cannot be blank" in line for line in self.out))

    def test_assign_resolved_ticket_rejected_at_id_field(self):
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        assign_ticket(self.tickets, "T001", "Sam")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")
        self.assertIsNone(menu_assign_ticket(self.tickets, scripted(["T001", "cancel"]), self.out.append))
        self.assertEqual(self.tickets[0]["assigned_to"], "Sam")
        self.assertTrue(any("reopen first" in line for line in self.out))

    def test_status_rejects_blank_and_unknown_status_immediately(self):
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        assign_ticket(self.tickets, "T001", "Sam")
        ticket = menu_update_status(self.tickets, scripted(["T001", "", "done", "In_Progress"]), self.out.append)
        self.assertEqual(ticket["status"], "in_progress")
        self.assertEqual(sum("Status must be" in line for line in self.out), 2)

    def test_unassigned_ticket_still_cannot_start_and_data_is_unchanged(self):
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        before = copy.deepcopy(self.tickets)
        result = menu_update_status(self.tickets, scripted(["T001", "in_progress"]), self.out.append)
        self.assertIsNone(result)
        self.assertTrue(any("Could not update status" in line for line in self.out))
        self.assertEqual(self.tickets, before)

    def test_view_ticket_reasks_until_ticket_exists(self):
        create_ticket(self.tickets, "WiFi down", "Network", "high", 12)
        ticket = menu_view_ticket(self.tickets, scripted(["", "T404", "t001"]), self.out.append)
        self.assertEqual(ticket["id"], "T001")
