import unittest
from pathlib import Path
from zoneinfo import ZoneInfo
from app.config import settings
from app.engine.parser import parse_ics_content
from app.ingestion.sync_service import MultiUserCalendarManager

class TestIngestion(unittest.TestCase):
    def setUp(self):
        self.tz = ZoneInfo("America/New_York")
        self.mgr = MultiUserCalendarManager()

    def test_parse_alice_calendar(self):
        alice_ics = (settings.BASE_DIR / "data" / "samples" / "alice.ics").read_text(encoding="utf-8")
        events = parse_ics_content(alice_ics, user_id="alice", provider="Apple Calendar", user_tz=self.tz)
        self.assertGreater(len(events), 0)
        
        # Verify specific events exist
        summaries = [e.summary for e in events]
        self.assertIn("CS 4900 Senior Capstone", summaries)
        self.assertIn("Coffee Meetup with Bob", summaries)
        self.assertIn("Campus Art Gallery Opening", summaries)

    def test_parse_bob_calendar(self):
        bob_ics = (settings.BASE_DIR / "data" / "samples" / "bob.ics").read_text(encoding="utf-8")
        events = parse_ics_content(bob_ics, user_id="bob", provider="Google Calendar", user_tz=self.tz)
        self.assertGreater(len(events), 0)
        summaries = [e.summary for e in events]
        self.assertIn("PHYS 2051 Physics Lecture", summaries)
        self.assertIn("Intramural Soccer Match", summaries)

    def test_multi_user_manager_initialization(self):
        self.assertIn("alice", self.mgr.users)
        self.assertIn("bob", self.mgr.users)
        self.assertIn("charlie", self.mgr.users)
        self.assertGreater(len(self.mgr.user_events.get("alice", [])), 0)
        self.assertGreater(len(self.mgr.user_events.get("bob", [])), 0)

    def test_add_calendar_feed(self):
        added = self.mgr.add_user_calendar_link("alice", "data/samples/bob.ics")
        self.assertTrue(added)
        self.assertIn("data/samples/bob.ics", self.mgr.users["alice"].calendar_urls)

if __name__ == "__main__":
    unittest.main()

