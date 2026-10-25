import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from app.config import settings
from app.engine.discord_router import (
    handle_incoming_discord_message,
    find_user_by_discord,
    clean_discord_handle,
    COLOR_BLURPLE,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_RED
)
from app.engine.mock_data import DISCORD_BOT_NAME, DISCORD_BOT_ID, DISCORD_DEFAULT_CHANNEL
from app.ingestion.sync_service import calendar_manager

class TestDiscordRouter(unittest.TestCase):
    def setUp(self):
        self.tz = ZoneInfo(settings.TIMEZONE)
        # Clean local store to avoid state carryover between test runs
        for p in settings.LOCAL_STORE_DIR.glob("*.ics"):
            try:
                p.unlink()
            except Exception:
                pass
        calendar_manager.refresh_all_calendars()
        self.alice_discord_id = "100000000000000001"
        self.alice_tag = "alice#1337"
        self.bob_discord_id = "100000000000000002"
        self.bob_tag = "bob#2024"
        self.charlie_discord_id = "100000000000000003"
        self.charlie_tag = "charlie#9090"

    def tearDown(self):
        for p in settings.LOCAL_STORE_DIR.glob("*.ics"):
            try:
                p.unlink()
            except Exception:
                pass
        calendar_manager.refresh_all_calendars()

    def test_find_user_by_discord(self):
        # Match by Discord ID
        user_by_id = find_user_by_discord(self.alice_discord_id)
        self.assertIsNotNone(user_by_id)
        self.assertEqual(user_by_id.id, "alice")

        # Match by full tag (e.g. alice#1337)
        user_by_tag = find_user_by_discord("alice#1337")
        self.assertIsNotNone(user_by_tag)
        self.assertEqual(user_by_tag.id, "alice")

        # Match by username before #
        user_by_name = find_user_by_discord("alice")
        self.assertIsNotNone(user_by_name)
        self.assertEqual(user_by_name.id, "alice")

        # Match by handle with @
        user_by_handle = find_user_by_discord("@bob")
        self.assertIsNotNone(user_by_handle)
        self.assertEqual(user_by_handle.id, "bob")

        # Match by mention format <@100000000000000001>
        user_by_mention = find_user_by_discord("<@100000000000000001>")
        self.assertIsNotNone(user_by_mention)
        self.assertEqual(user_by_mention.id, "alice")

    def test_agenda_command(self):
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="!agenda 2026-10-16"
        )
        self.assertEqual(meta.get("action"), "agenda")
        self.assertIn("Agenda", reply)
        self.assertIsNotNone(embed)
        self.assertIn("Agenda", embed["title"])
        self.assertEqual(embed["color"], COLOR_BLURPLE)

    def test_free_availability_command(self):
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="!free @bob 2026-10-16"
        )
        self.assertEqual(meta.get("action"), "free_query")
        self.assertIn("Mutual Free Time", reply)
        self.assertIsNotNone(embed)
        self.assertIn("Mutual Availability", embed["title"])
        self.assertTrue(len(embed["fields"]) > 0)

    def test_meet_scheduling_command_success(self):
        # 15:00 to 16:00 is mutual free for Alice & Bob on 2026-10-16
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="!meet @bob 2026-10-16 15:00-16:00 Capstone Strategy"
        )
        self.assertEqual(meta.get("action"), "meet_scheduled")
        self.assertIn("Confirmed & Added to Calendars", reply)
        self.assertIn("Capstone Strategy", reply)
        self.assertIsNotNone(embed)
        self.assertEqual(embed["color"], COLOR_GREEN)
        self.assertIn("Capstone Strategy", embed["title"])

    def test_meet_collision_detection(self):
        # Bob has Intramural Soccer from 17:00 to 18:30 on 2026-10-16
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="!meet @bob 2026-10-16 17:30-18:00 Quick Catchup"
        )
        self.assertEqual(meta.get("action"), "meet_conflict")
        self.assertIn("Collision detected", reply)
        self.assertIn("Bob Martinez", reply)
        self.assertIsNotNone(embed)
        self.assertEqual(embed["color"], COLOR_YELLOW)
        self.assertIn("Conflict Detected", embed["title"])

    def test_privacy_command(self):
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.charlie_discord_id,
            content="!privacy OPEN"
        )
        self.assertEqual(meta.get("action"), "privacy")
        self.assertEqual(meta.get("new_mode"), "transparent")
        self.assertIn("Transparent", reply)
        self.assertIsNotNone(embed)
        self.assertIn("Privacy", embed["title"])

    def test_photo_attachment_moment(self):
        initial_posts = len(calendar_manager.posts)
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="Testing photo moment via Discord 📸",
            attachment_url="/static/images/darkroom_photo.svg"
        )
        self.assertEqual(meta.get("status"), "discord_moment_posted")
        self.assertIn("posted", reply)
        self.assertEqual(len(calendar_manager.posts), initial_posts + 1)
        self.assertEqual(calendar_manager.posts[0].photo_url, "/static/images/darkroom_photo.svg")
        self.assertIsNotNone(embed)
        self.assertEqual(embed["image"]["url"], "/static/images/darkroom_photo.svg")

    def test_unregistered_discord_user(self):
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier="999999999999999999",
            content="!agenda"
        )
        self.assertEqual(meta.get("status"), "unregistered_sender")
        self.assertIn("not connected", reply)
        self.assertIsNotNone(embed)
        self.assertEqual(embed["color"], COLOR_RED)

    def test_slash_command_support(self):
        # Support / prefix in addition to ! prefix
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="/free @bob 2026-10-16"
        )
        self.assertEqual(meta.get("action"), "free_query")
        self.assertIn("Mutual Free Time", reply)

    def test_help_command(self):
        reply, embed, meta = handle_incoming_discord_message(
            sender_identifier=self.alice_discord_id,
            content="!help"
        )
        self.assertEqual(meta.get("action"), "help")
        self.assertIn("CalMedia Discord Bot", reply)
        self.assertIsNotNone(embed)
        self.assertTrue(len(embed["fields"]) >= 4)

if __name__ == "__main__":
    unittest.main()

