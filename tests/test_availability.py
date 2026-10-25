import unittest
from datetime import date
from zoneinfo import ZoneInfo
from app.engine.availability import compute_group_availability, check_preflight_conflicts
from app.ingestion.sync_service import MultiUserCalendarManager

class TestAvailability(unittest.TestCase):
    def setUp(self):
        self.tz = ZoneInfo("America/New_York")
        self.mgr = MultiUserCalendarManager()
        self.target_date = date(2026, 10, 16)  # Friday

    def test_group_availability_overlap(self):
        result = compute_group_availability(
            target_date=self.target_date,
            users=self.mgr.users,
            events_by_user=self.mgr.user_events,
            participant_ids=["alice", "bob", "charlie"],
            user_tz=self.tz
        )
        self.assertEqual(result.target_date, "2026-10-16")
        self.assertEqual(result.participants, ["alice", "bob", "charlie"])
        
        # Verify mutual free slots exist
        self.assertGreater(len(result.mutual_free_slots), 0)
        # Verify 15:00 - 17:00 is an open block for all three
        slot_spans = [(s.start, s.end) for s in result.mutual_free_slots]
        # Should contain an afternoon window ending at or around 17:00 (when Bob's soccer starts)
        afternoon_free = any(s.start >= "15:00" and s.end <= "17:00" for s in result.mutual_free_slots)
        self.assertTrue(afternoon_free)

    def test_privacy_masking_for_busy_only_user(self):
        # Charlie is initialized with privacy_mode="busy_only"
        result = compute_group_availability(
            target_date=self.target_date,
            users=self.mgr.users,
            events_by_user=self.mgr.user_events,
            participant_ids=["charlie"],
            user_tz=self.tz
        )
        charlie_events = result.user_busy_intervals["charlie"]
        for ev in charlie_events:
            self.assertEqual(ev["summary"], "🔒 Busy")
            self.assertEqual(ev["location"], "")
            self.assertTrue(ev["is_masked"])

    def test_preflight_conflict_detection(self):
        # Bob has Intramural Soccer from 17:00 to 18:30 on 2026-10-16
        conflict_res = check_preflight_conflicts(
            target_date=self.target_date,
            start_time_str="17:30",
            end_time_str="18:00",
            participant_ids=["alice", "bob"],
            events_by_user=self.mgr.user_events,
            users=self.mgr.users,
            user_tz=self.tz
        )
        self.assertFalse(conflict_res.is_conflict_free)
        self.assertGreater(len(conflict_res.conflicts), 0)
        self.assertEqual(conflict_res.conflicts[0]["user_id"], "bob")

    def test_preflight_conflict_free_slot(self):
        # 15:30 to 16:30 is mutual free for Alice and Bob
        free_res = check_preflight_conflicts(
            target_date=self.target_date,
            start_time_str="15:30",
            end_time_str="16:30",
            participant_ids=["alice", "bob"],
            events_by_user=self.mgr.user_events,
            users=self.mgr.users,
            user_tz=self.tz
        )
        self.assertTrue(free_res.is_conflict_free)
        self.assertEqual(len(free_res.conflicts), 0)

if __name__ == "__main__":
    unittest.main()

