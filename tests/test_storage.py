import unittest, tempfile, os, json
from campusflow.storage import load_tickets

class TestStorage(unittest.TestCase):
    def test_duplicate_id_rejects_no_state_loss(self):
        tickets=[{"id":"T001","title":"a","category":"Network","urgency":"high","affected_users":1,"priority":"critical","status":"open","assigned_to":None,"notes":[]},
                 {"id":"T001","title":"b","category":"Network","urgency":"high","affected_users":1,"priority":"critical","status":"open","assigned_to":None,"notes":[]}]
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(tickets,f)
            path=f.name
        try:
            with self.assertRaises(ValueError):
                load_tickets(path)
        finally:
            os.unlink(path)

    def test_corrupt_json_rejects(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("{ corrupt")
            path=f.name
        try:
            with self.assertRaises(ValueError):
                load_tickets(path)
        finally:
            os.unlink(path)
