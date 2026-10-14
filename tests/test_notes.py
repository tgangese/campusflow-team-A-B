import unittest
from campusflow.tickets import create_ticket
from campusflow.notes import add_note

class TestNotes(unittest.TestCase):
    def test_valid_note_id(self):
        tickets=[]
        t=create_ticket(tickets,"WiFi down","Network","high",5)
        n=add_note(tickets,t["id"],"Mentor A","Router reboot attempted")
        self.assertEqual(n["note_id"],"N001")
    def test_blank_note_no_id_consume(self):
        tickets=[]
        t=create_ticket(tickets,"WiFi","Network","high",5)
        add_note(tickets,t["id"],"A","Valid message here")
        with self.assertRaises(ValueError):
            add_note(tickets,t["id"],"A","hi")
        n2=add_note(tickets,t["id"],"B","Second valid note message")
        self.assertEqual(n2["note_id"],"N002")
    def test_resolved_rejects(self):
        tickets=[]
        t=create_ticket(tickets,"WiFi","Network","high",5)
        t["status"]="resolved"
        with self.assertRaises(ValueError):
            add_note(tickets,t["id"],"A","Should fail")
