import unittest
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, update_ticket_status

class TestTicketAssignment(unittest.TestCase):
    def setUp(self):
        self.tickets=[]
        self.ticket=create_ticket(self.tickets,"WiFi","Network","high",5)

    def test_assign_ticket_successfully(self):
        t=assign_ticket(self.tickets,"T001","Alice")
        self.assertEqual(t["assigned_to"],"Alice")
    def test_assign_ticket_strips_staff_name(self):
        t=assign_ticket(self.tickets,"T001"," Alice ")
        self.assertEqual(t["assigned_to"],"Alice")
    def test_blank_staff_name_raises_error(self):
        with self.assertRaises(ValueError): assign_ticket(self.tickets,"T001"," ")
    def test_non_string_staff_name_raises_error(self):
        with self.assertRaises(ValueError): assign_ticket(self.tickets,"T001",123)
    def test_assign_unknown_ticket_raises_error(self):
        with self.assertRaises(ValueError): assign_ticket(self.tickets,"T999","Bob")

class TestTicketStatusWorkflow(unittest.TestCase):
    def setUp(self):
        self.tickets=[]
        self.ticket=create_ticket(self.tickets,"WiFi","Network","high",5)
        assign_ticket(self.tickets,"T001","Alice")

    def test_open_ticket_moves_to_in_progress(self):
        ticket=update_ticket_status(self.tickets,"T001","in_progress")
        self.assertEqual(ticket["status"],"in_progress")
    def test_in_progress_ticket_moves_to_resolved(self):
        update_ticket_status(self.tickets,"T001","in_progress")
        ticket=update_ticket_status(self.tickets,"T001","resolved")
        self.assertEqual(ticket["status"],"resolved")
    def test_in_progress_ticket_can_return_to_open(self):
        update_ticket_status(self.tickets,"T001","in_progress")
        ticket=update_ticket_status(self.tickets,"T001","open")
        self.assertEqual(ticket["status"],"open")
    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError): update_ticket_status(self.tickets,"T001","invalid")
    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(ValueError): update_ticket_status(self.tickets,"T001","resolved")
    def test_resolved_can_be_reopened(self):
        update_ticket_status(self.tickets,"T001","in_progress")
        update_ticket_status(self.tickets,"T001","resolved")
        ticket=update_ticket_status(self.tickets,"T001","open")
        self.assertEqual(ticket["status"],"open")
    def test_status_is_case_insensitive(self):
        ticket=update_ticket_status(self.tickets,"T001","IN_PROGRESS")
        self.assertEqual(ticket["status"],"in_progress")
    def test_unknown_ticket_is_rejected(self):
        with self.assertRaises(ValueError): update_ticket_status(self.tickets,"T999","open")
    def test_unassigned_open_cannot_go_in_progress(self):
        tickets=[]
        t=create_ticket(tickets,"WiFi","Network","high",5)
        with self.assertRaises(ValueError): update_ticket_status(tickets,t["id"],"in_progress")
