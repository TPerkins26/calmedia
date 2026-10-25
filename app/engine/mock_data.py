from typing import Dict, List
from app.models import UserProfile, SocialPost

DISCORD_BOT_NAME = "CalMedia Bot"
DISCORD_BOT_ID = "999999999999999999"
DISCORD_DEFAULT_CHANNEL = "#calendar-sync"

def get_seed_users() -> Dict[str, UserProfile]:
    return {
        "alice": UserProfile(
            id="alice",
            name="Alice Chen",
            handle="@alice",
            avatar="👩‍🎨",
            bio="Visual arts & CS Senior. Coffee lover, film photography, and UI design.",
            calendar_urls=["data/samples/alice.ics"],
            privacy_mode="transparent",
            friends=["bob", "charlie"],
            discord_username="alice#1337",
            discord_id="100000000000000001"
        ),
        "bob": UserProfile(
            id="bob",
            name="Bob Martinez",
            handle="@bob",
            avatar="🏃‍♂️",
            bio="Physics major, intramural soccer captain. Always looking for study buddies.",
            calendar_urls=["data/samples/bob.ics"],
            privacy_mode="transparent",
            friends=["alice", "charlie"],
            discord_username="bob#2024",
            discord_id="100000000000000002"
        ),
        "charlie": UserProfile(
            id="charlie",
            name="Charlie Taylor",
            handle="@charlie",
            avatar="📚",
            bio="Psychology & HCI research. Quiet hours at Alden Library.",
            calendar_urls=["data/samples/charlie.ics"],
            privacy_mode="busy_only",  # Tests privacy masking!
            friends=["alice", "bob"],
            discord_username="charlie#9090",
            discord_id="100000000000000003"
        ),
    }

def get_seed_posts() -> List[SocialPost]:
    return [
        SocialPost(
            id="post-alice-1",
            author_id="alice",
            author_name="Alice Chen",
            author_handle="@alice",
            author_avatar="👩‍🎨",
            is_verified_event=True,
            event_uid="alice-photo-lab",
            event_summary="Digital Photography Studio Lab",
            event_start="2026-10-15T14:00:00",
            event_end="2026-10-15T16:00:00",
            event_location="Seigfred Hall Darkroom",
            event_provider="Apple Calendar",
            photo_url="/static/images/darkroom_photo.svg",
            caption="First batch of 35mm prints dried in the darkroom today! 🎞️✨ Ready for the gallery critique tomorrow evening.",
            created_at="2026-10-15T16:15:00",
            privacy="public",
            likes=14
        ),
        SocialPost(
            id="post-bob-1",
            author_id="bob",
            author_name="Bob Martinez",
            author_handle="@bob",
            author_avatar="🏃‍♂️",
            is_verified_event=True,
            event_uid="bob-soccer-fri",
            event_summary="Intramural Soccer Match",
            event_start="2026-10-16T17:00:00",
            event_end="2026-10-16T18:30:00",
            event_location="Mill Street Recreation Fields",
            event_provider="Google Calendar",
            photo_url="/static/images/soccer_photo.svg",
            caption="Intense semifinal match under the autumn lights! ⚽ Took the win 3-2. Now resting up for the weekend.",
            created_at="2026-10-16T18:45:00",
            privacy="public",
            likes=21
        ),
        SocialPost(
            id="post-alice-2",
            author_id="alice",
            author_name="Alice Chen",
            author_handle="@alice",
            author_avatar="👩‍🎨",
            is_verified_event=False,
            event_uid=None,
            event_summary="Spontaneous Coffee Break on College Green",
            event_start="2026-10-16T11:00:00",
            event_end="2026-10-16T11:45:00",
            event_location="Front Room Coffeehouse",
            event_provider="Manual",
            photo_url="/static/images/coffee_photo.svg",
            caption="Spontaneous iced matcha break before afternoon capstone 🍵 Check my availability tab if you want to hang out after 3 PM!",
            created_at="2026-10-16T11:30:00",
            privacy="public",
            likes=9
        )
    ]

