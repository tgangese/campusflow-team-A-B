import unittest
from campusflow.tickets import calculate_priority, create_ticket, validate_affected_users

class TestPriorityEngine(unittest.TestCase):
    def test_high_12_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")
    
    def test_high_2_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")
    
    def test_low_4_medium(self):
        self.assertEqual(calculate_priority("low", 4), "medium")
    
    def test_low_1_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")
    
    def test_rule_order_critical_over_high(self):
        # This test catches AI mistake: if OR checked before AND, high+10 would be high not critical
        self.assertEqual(calculate_priority("high", 10), "critical")
    
    def test_medium_10_high(self):
        self.assertEqual(calculate_priority("medium", 10), "high")
    
    def test_medium_3_medium(self):
        self.assertEqual(calculate_priority("medium", 3), "medium")

class TestTicketCreation(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_create_valid(self):
        t = create_ticket(self.tickets, "WiFi down", "Network", "high", 15)
        self.assertEqual(t["id"], "T001")
        self.assertEqual(t["priority"], "critical")
        self.assertEqual(t["status"], "open")

    def test_zero_users_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Test", "Network", "low", 0)

    def test_blank_title_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "   ", "Network", "low", 1)

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Test", "InvalidCat", "low", 1)

    def test_normalize_case(self):
        t = create_ticket(self.tickets, "Test", "NETWORK", "High", 1)
        self.assertEqual(t["category"], "Network")
        self.assertEqual(t["urgency"], "high")

    def test_decimal_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users("3.5")

    def test_id_increment(self):
        create_ticket(self.tickets, "A", "Network", "low", 1)
        t2 = create_ticket(self.tickets, "B", "Network", "low", 1)
        self.assertEqual(t2["id"], "T002")

if __name__ == "__main__":
    unittest.main()