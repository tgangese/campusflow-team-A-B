import unittest
from campusflow.validation import validate_affected_users, validate_category

class TestValidation(unittest.TestCase):
    def test_reject_bool_affected(self):
        with self.assertRaises(ValueError):
            validate_affected_users(True)
    def test_reject_float(self):
        with self.assertRaises(ValueError):
            validate_affected_users(2.5)
    def test_reject_zero(self):
        with self.assertRaises(ValueError):
            validate_affected_users(0)
    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            validate_category("InvalidCat")
