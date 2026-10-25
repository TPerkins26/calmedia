import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from app.config import settings
from app.models import SocialPost
from app.ingestion.sync_service import MultiUserCalendarManager
from app.writers.local_writer import save_event_to_local_store, generate_ics_invite

class TestSocial(unittest.TestCase):
    def setUp(self):
        self.tz = ZoneInfo("America/New_York")
        self.mgr = MultiUserCalendarManager()

    def tearDown(self):
        # Clean up test local store files
        test_store = settings.LOCAL_STORE_DIR / "test_user.ics"
        if test_store.exists():
            test_store.unlink()

    def test_create_verified_post(self):
        post = SocialPost(
            id="test-post-1",
            author_id="alice",
            author_name="Alice Chen",
            author_handle="@alice",
            author_avatar="👩‍🎨",
            is_verified_event=True,
            event_uid="alice-photo-lab",
            event_summary="Digital Photography Studio Lab",
            photo_url="/static/images/darkroom_photo.svg",
            caption="Testing darkroom photo post!",
            created_at=datetime.now(self.tz).isoformat()
        )
        self.mgr.add_post(post)
        self.assertEqual(self.mgr.posts[0].id, "test-post-1")
        self.assertTrue(self.mgr.posts[0].is_verified_event)

    def test_like_post(self):
        post = self.mgr.posts[0]
        initial_likes = post.likes
        new_likes = self.mgr.like_post(post.id)
        self.assertEqual(new_likes, initial_likes + 1)

    def test_local_write_and_ics_generation(self):
        start = datetime(2026, 10, 16, 15, 0, tzinfo=self.tz)
        end = datetime(2026, 10, 16, 16, 30, tzinfo=self.tz)
        
        # Test RFC 5545 invite generation
        ics = generate_ics_invite(
            uid="test-group-meet",
            title="Design Sprint & Coffee",
            start_dt=start,
            end_dt=end,
            location="Front Room",
            description="Discuss capstone",
            attendees=["alice", "bob"]
        )
        self.assertIn("BEGIN:VCALENDAR", ics)
        self.assertIn("SUMMARY:Design Sprint & Coffee", ics)
        self.assertIn("ATTENDEE;CN=alice:mailto:alice@example.edu", ics)
        self.assertIn("END:VCALENDAR", ics)

        # Test writing to local store
        store_path = save_event_to_local_store(
            user_id="test_user",
            uid="test-group-meet-store",
            title="Design Sprint & Coffee",
            start_dt=start,
            end_dt=end
        )
        self.assertTrue(store_path.exists())
        content = store_path.read_text(encoding="utf-8")
        self.assertIn("test-group-meet-store", content)

    def test_account_creation(self):
        new_user = self.mgr.create_user({
            "name": "Maya Lin",
            "handle": "maya",
            "avatar": "👩‍💻",
            "bio": "Architecture & CS junior.",
            "discord_username": "maya#4040",
            "calendar_url": "data/samples/alice.ics"
        })
        self.assertIn(new_user.id, self.mgr.users)
        self.assertEqual(new_user.name, "Maya Lin")
        self.assertTrue(new_user.handle.startswith("@"))
        self.assertEqual(new_user.discord_username, "maya#4040")
        self.assertTrue(len(new_user.calendar_urls) > 0)
        self.assertIn(new_user.id, self.mgr.user_events)

    def test_networking_between_two_people(self):
        # Create user 1 and user 2
        user_a = self.mgr.create_user({"name": "User Alpha", "handle": "@alpha", "avatar": "🅰️"})
        user_b = self.mgr.create_user({"name": "User Beta", "handle": "@beta", "avatar": "🅱️"})

        # Alpha sends friend request to Beta
        res1 = self.mgr.send_friend_request(user_a.id, user_b.id)
        self.assertEqual(res1["status"], "request_sent")
        self.assertIn(user_b.id, user_a.outgoing_requests)
        self.assertIn(user_a.id, user_b.incoming_requests)

        # Network relationship check from Beta's perspective
        net_b = self.mgr.get_user_network(user_b.id)
        incoming_ids = [u["id"] for u in net_b["incoming"]]
        self.assertIn(user_a.id, incoming_ids)

        # Beta accepts request
        res2 = self.mgr.accept_friend_request(user_b.id, user_a.id)
        self.assertEqual(res2["status"], "mutual_connected")
        self.assertIn(user_b.id, user_a.friends)
        self.assertIn(user_a.id, user_b.friends)

        # Network check confirms mutual friends
        net_a = self.mgr.get_user_network(user_a.id)
        friend_ids = [u["id"] for u in net_a["friends"]]
        self.assertIn(user_b.id, friend_ids)

        # Unfriend test
        res3 = self.mgr.unfriend(user_a.id, user_b.id)
        self.assertEqual(res3["status"], "unfriended")
        self.assertNotIn(user_b.id, user_a.friends)
        self.assertNotIn(user_a.id, user_b.friends)

    def test_reciprocal_friend_request_auto_connect(self):
        user_c = self.mgr.create_user({"name": "User Charlie", "handle": "@charlie2"})
        user_d = self.mgr.create_user({"name": "User Delta", "handle": "@delta"})

        # C requests D
        self.mgr.send_friend_request(user_c.id, user_d.id)
        # D requests C -> should automatically resolve to mutual_connected
        res = self.mgr.send_friend_request(user_d.id, user_c.id)
        self.assertEqual(res["status"], "mutual_connected")
        self.assertIn(user_d.id, user_c.friends)
        self.assertIn(user_c.id, user_d.friends)

if __name__ == "__main__":
    unittest.main()

