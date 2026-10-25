import os
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional
from datetime import datetime

from app.config import settings
from app.models import UserProfile, CalendarEvent, SocialPost
from app.engine.parser import parse_ics_content
from app.engine.mock_data import get_seed_users, get_seed_posts

class MultiUserCalendarManager:
    """
    Manages user profiles, shareable calendar link ingestion,
    caching, and social posts.
    """
    def __init__(self):
        self.users: Dict[str, UserProfile] = get_seed_users()
        self.posts: List[SocialPost] = get_seed_posts()
        self.user_events: Dict[str, List[CalendarEvent]] = {}
        self.user_tz = ZoneInfo(settings.TIMEZONE)
        self.last_sync_time: Optional[str] = None
        self.refresh_all_calendars()

    def refresh_user_calendar(self, user_id: str):
        """Fetches and parses all calendar feeds and local store entries for a user."""
        user = self.users.get(user_id)
        if not user:
            return

        aggregated_events: List[CalendarEvent] = []
        cache_user_dir = settings.CACHE_DIR / user_id
        cache_user_dir.mkdir(parents=True, exist_ok=True)

        for idx, url in enumerate(user.calendar_urls):
            ics_text = ""
            provider_label = "Shareable Feed"
            if "google" in url.lower():
                provider_label = "Google Calendar"
            elif "icloud" in url.lower() or "apple" in url.lower():
                provider_label = "Apple Calendar"
            elif "outlook" in url.lower() or "office" in url.lower():
                provider_label = "Microsoft Outlook"
            elif "canvas" in url.lower():
                provider_label = "Canvas LMS"

            # Check if local sample file
            if url.startswith("data/") or Path(url).exists():
                local_path = settings.BASE_DIR / url if not Path(url).is_absolute() else Path(url)
                if local_path.exists():
                    try:
                        ics_text = local_path.read_text(encoding="utf-8")
                    except Exception as e:
                        print(f"Error reading local calendar {local_path}: {e}")
            elif url.startswith("http://") or url.startswith("https://") or url.startswith("webcal://"):
                fetch_url = url.replace("webcal://", "https://")
                cache_file = cache_user_dir / f"feed_{idx}.ics"
                try:
                    req = urllib.request.Request(fetch_url, headers={"User-Agent": "CalendarSocialMedia/1.0"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        ics_text = resp.read().decode("utf-8", errors="replace")
                    cache_file.write_text(ics_text, encoding="utf-8")
                except Exception as e:
                    print(f"Warning: Failed to fetch {fetch_url}: {e}. Trying cache.")
                    if cache_file.exists():
                        ics_text = cache_file.read_text(encoding="utf-8")

            if ics_text:
                parsed = parse_ics_content(
                    ics_text=ics_text,
                    user_id=user_id,
                    provider=provider_label,
                    user_tz=self.user_tz
                )
                aggregated_events.extend(parsed)

        # Ingest local mock write store if it exists
        local_store_path = settings.LOCAL_STORE_DIR / f"{user_id}.ics"
        if local_store_path.exists():
            store_text = local_store_path.read_text(encoding="utf-8")
            store_events = parse_ics_content(
                ics_text=store_text,
                user_id=user_id,
                provider="Scheduled (Local Store)",
                user_tz=self.user_tz
            )
            aggregated_events.extend(store_events)

        aggregated_events.sort(key=lambda e: e.start)
        self.user_events[user_id] = aggregated_events

    def refresh_all_calendars(self):
        """Refreshes calendars for all registered users."""
        for uid in list(self.users.keys()):
            self.refresh_user_calendar(uid)
        self.last_sync_time = datetime.now(self.user_tz).strftime("%I:%M %p")

    def add_user_calendar_link(self, user_id: str, shareable_url: str) -> bool:
        """Links a new shareable calendar link to a user."""
        if user_id not in self.users:
            return False
        if shareable_url not in self.users[user_id].calendar_urls:
            self.users[user_id].calendar_urls.append(shareable_url)
            self.refresh_user_calendar(user_id)
            return True
        return False

    def toggle_privacy_mode(self, user_id: str) -> str:
        """Toggles between transparent and busy_only mode."""
        if user_id not in self.users:
            return "transparent"
        cur = self.users[user_id].privacy_mode
        new_mode = "busy_only" if cur == "transparent" else "transparent"
        self.users[user_id].privacy_mode = new_mode
        return new_mode

    def add_post(self, post: SocialPost):
        """Adds a new social post to the head of the feed."""
        self.posts.insert(0, post)

    def like_post(self, post_id: str) -> int:
        for p in self.posts:
            if p.id == post_id:
                p.likes += 1
                return p.likes
        return 0

    def create_user(self, data: Dict[str, Any]) -> UserProfile:
        """Creates a new user profile with optional initial calendar link."""
        raw_name = data.get("name", "").strip() or "New Student"
        raw_handle = data.get("handle", "").strip() or f"@{raw_name.lower().replace(' ', '')}"
        if not raw_handle.startswith("@"):
            raw_handle = "@" + raw_handle

        user_id = data.get("id") or raw_handle.replace("@", "").lower().replace(" ", "_")
        # Ensure unique id
        base_id = user_id
        counter = 1
        while user_id in self.users:
            user_id = f"{base_id}_{counter}"
            counter += 1

        avatar = data.get("avatar") or "🎓"
        bio = data.get("bio", "Student at Ohio University.")
        privacy = data.get("privacy_mode", "transparent")
        discord_username = data.get("discord_username", f"{user_id}#1000")
        discord_id = data.get("discord_id", f"{abs(hash(user_id)) % 10**18}")
        calendar_url = data.get("calendar_url", "").strip()

        calendar_urls = [calendar_url] if calendar_url else []

        new_user = UserProfile(
            id=user_id,
            name=raw_name,
            handle=raw_handle,
            avatar=avatar,
            bio=bio,
            calendar_urls=calendar_urls,
            privacy_mode=privacy,
            friends=[],
            incoming_requests=[],
            outgoing_requests=[],
            discord_username=discord_username,
            discord_id=discord_id
        )

        self.users[user_id] = new_user
        self.user_events[user_id] = []
        if calendar_urls:
            self.refresh_user_calendar(user_id)

        return new_user

    def send_friend_request(self, from_uid: str, to_uid: str) -> Dict[str, Any]:
        """Sends a friend request between two users, or automatically connects if reciprocal."""
        if from_uid not in self.users or to_uid not in self.users:
            return {"error": "User not found", "status": "error"}
        if from_uid == to_uid:
            return {"error": "Cannot friend yourself", "status": "error"}

        from_user = self.users[from_uid]
        to_user = self.users[to_uid]

        if to_uid in from_user.friends:
            return {"status": "already_friends", "message": f"Already mutual friends with {to_user.name}"}

        # If to_user already requested from_user, automatically accept & connect!
        if to_uid in from_user.incoming_requests:
            return self.accept_friend_request(from_uid, to_uid)

        if to_uid not in from_user.outgoing_requests:
            from_user.outgoing_requests.append(to_uid)
        if from_uid not in to_user.incoming_requests:
            to_user.incoming_requests.append(from_uid)

        return {
            "status": "request_sent",
            "message": f"Friend request sent to {to_user.name} ({to_user.handle})",
            "from_id": from_uid,
            "to_id": to_uid
        }

    def accept_friend_request(self, user_id: str, requester_id: str) -> Dict[str, Any]:
        """Accepts an incoming friend request, establishing mutual friendship."""
        if user_id not in self.users or requester_id not in self.users:
            return {"error": "User not found", "status": "error"}

        user = self.users[user_id]
        requester = self.users[requester_id]

        if requester_id not in user.friends:
            user.friends.append(requester_id)
        if user_id not in requester.friends:
            requester.friends.append(user_id)

        if requester_id in user.incoming_requests:
            user.incoming_requests.remove(requester_id)
        if user_id in requester.outgoing_requests:
            requester.outgoing_requests.remove(user_id)
        if requester_id in user.outgoing_requests:
            user.outgoing_requests.remove(requester_id)
        if user_id in requester.incoming_requests:
            requester.incoming_requests.remove(user_id)

        return {
            "status": "mutual_connected",
            "message": f"You and {requester.name} are now mutual friends!",
            "friends": user.friends
        }

    def decline_friend_request(self, user_id: str, requester_id: str) -> Dict[str, Any]:
        """Declines/cancels an incoming friend request."""
        if user_id not in self.users or requester_id not in self.users:
            return {"error": "User not found", "status": "error"}

        user = self.users[user_id]
        requester = self.users[requester_id]

        if requester_id in user.incoming_requests:
            user.incoming_requests.remove(requester_id)
        if user_id in requester.outgoing_requests:
            requester.outgoing_requests.remove(user_id)

        return {"status": "declined", "message": f"Request from {requester.name} declined"}

    def unfriend(self, user_id: str, target_id: str) -> Dict[str, Any]:
        """Removes friendship between two users."""
        if user_id not in self.users or target_id not in self.users:
            return {"error": "User not found", "status": "error"}

        user = self.users[user_id]
        target = self.users[target_id]

        if target_id in user.friends:
            user.friends.remove(target_id)
        if user_id in target.friends:
            target.friends.remove(user_id)

        return {"status": "unfriended", "message": f"Removed {target.name} from friends"}

    def get_user_network(self, viewer_id: str) -> Dict[str, Any]:
        """Returns full network relationships from perspective of viewer_id."""
        viewer = self.users.get(viewer_id)
        if not viewer:
            return {"friends": [], "incoming": [], "outgoing": [], "all_users": []}

        friends_list = []
        incoming_list = []
        outgoing_list = []
        all_campus = []

        for uid, u in self.users.items():
            u_dict = u.to_dict()
            is_self = (uid == viewer_id)
            is_friend = (uid in viewer.friends)
            is_incoming = (uid in viewer.incoming_requests)
            is_outgoing = (uid in viewer.outgoing_requests)

            user_meta = {
                **u_dict,
                "is_self": is_self,
                "is_friend": is_friend,
                "is_incoming": is_incoming,
                "is_outgoing": is_outgoing,
                "event_count": len(self.user_events.get(uid, []))
            }

            if not is_self:
                all_campus.append(user_meta)
                if is_friend:
                    friends_list.append(user_meta)
                elif is_incoming:
                    incoming_list.append(user_meta)
                elif is_outgoing:
                    outgoing_list.append(user_meta)

        return {
            "viewer_id": viewer_id,
            "friends": friends_list,
            "incoming": incoming_list,
            "outgoing": outgoing_list,
            "all_campus": all_campus
        }

calendar_manager = MultiUserCalendarManager()

