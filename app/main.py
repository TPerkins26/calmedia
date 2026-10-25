import os
import json
import uuid
import mimetypes
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Dict, Any, List

from app.config import settings
from app.models import SocialPost, CalendarEvent
from app.ingestion.sync_service import calendar_manager
from app.engine.availability import compute_group_availability, check_preflight_conflicts
from app.writers.local_writer import save_event_to_local_store, generate_ics_invite
from app.engine.discord_router import handle_incoming_discord_message, find_user_by_discord
from app.engine.mock_data import DISCORD_BOT_NAME, DISCORD_BOT_ID, DISCORD_DEFAULT_CHANNEL

# Pre-generate in-memory state or read from manager
user_tz = ZoneInfo(settings.TIMEZONE)

# In-memory Discord channel log for interactive simulator
discord_logs: List[Dict[str, Any]] = [
    {
        "id": "msg-seed-1",
        "timestamp": datetime.now(user_tz).strftime("%I:%M %p"),
        "author": {
            "id": "100000000000000001",
            "username": "alice#1337",
            "name": "Alice Chen",
            "avatar": "👩‍🎨",
            "bot": False
        },
        "channel": DISCORD_DEFAULT_CHANNEL,
        "content": "!free @bob",
        "attachment_url": None,
        "embed": None
    },
    {
        "id": "msg-seed-2",
        "timestamp": datetime.now(user_tz).strftime("%I:%M %p"),
        "author": {
            "id": DISCORD_BOT_ID,
            "username": "CalMedia Bot#0001",
            "name": DISCORD_BOT_NAME,
            "avatar": "🤖",
            "bot": True
        },
        "channel": DISCORD_DEFAULT_CHANNEL,
        "content": "✨ **Mutual Free Time for Alice Chen, Bob Martinez** (today):\n• `11:30 - 12:00` (30m)\n• `15:00 - 17:00` (120m) (🔥 Prime)\nTo book: `!meet @friend HH:MM-HH:MM Title`",
        "attachment_url": None,
        "embed": {
            "title": "✨ Mutual Availability (today)",
            "description": "Found **2 open windows** between **Alice Chen, Bob Martinez**:",
            "color": 0x5865F2,
            "fields": [
                {"name": "11:30 – 12:00", "value": "30 mins free", "inline": True},
                {"name": "15:00 – 17:00", "value": "120 mins free (🔥 Prime)", "inline": True}
            ],
            "footer": {"text": "CalMedia Bot • To schedule: !meet @friend HH:MM-HH:MM [Title] • #calendar-sync"}
        }
    }
]

def handle_get_users():
    return {uid: u.to_dict() for uid, u in calendar_manager.users.items()}

def handle_get_user(user_id: str):
    if user_id not in calendar_manager.users:
        return {"error": "User not found"}, 404
    return calendar_manager.users[user_id].to_dict(), 200

def handle_create_user(data: Dict[str, Any]):
    new_user = calendar_manager.create_user(data)
    return new_user.to_dict(), 201

def handle_get_network(viewer_id: str):
    network = calendar_manager.get_user_network(viewer_id)
    return network, 200

def handle_connect_friend(user_id: str, data: Dict[str, Any]):
    target_id = data.get("target_id", "")
    res = calendar_manager.send_friend_request(user_id, target_id)
    code = 400 if "error" in res else 200
    return res, code

def handle_accept_friend(user_id: str, data: Dict[str, Any]):
    requester_id = data.get("requester_id", "")
    res = calendar_manager.accept_friend_request(user_id, requester_id)
    code = 400 if "error" in res else 200
    return res, code

def handle_decline_friend(user_id: str, data: Dict[str, Any]):
    requester_id = data.get("requester_id", "")
    res = calendar_manager.decline_friend_request(user_id, requester_id)
    code = 400 if "error" in res else 200
    return res, code

def handle_unfriend(user_id: str, data: Dict[str, Any]):
    target_id = data.get("target_id", "")
    res = calendar_manager.unfriend(user_id, target_id)
    code = 400 if "error" in res else 200
    return res, code

def handle_toggle_privacy(user_id: str):
    if user_id not in calendar_manager.users:
        return {"error": "User not found"}, 404
    new_mode = calendar_manager.toggle_privacy_mode(user_id)
    return {"user_id": user_id, "privacy_mode": new_mode}, 200

def handle_get_user_events(user_id: str, viewer_id: str = ""):
    if user_id not in calendar_manager.users:
        return {"error": "User not found"}, 404
    events = calendar_manager.user_events.get(user_id, [])
    user = calendar_manager.users[user_id]
    
    # If viewer is not the user and privacy is busy_only, mask details
    mask = (viewer_id != user_id and user.privacy_mode == "busy_only")
    out = []
    for e in events:
        d = e.to_dict()
        if mask:
            d["summary"] = "🔒 Busy"
            d["location"] = ""
            d["description"] = ""
            d["is_masked"] = True
        else:
            d["is_masked"] = False
        out.append(d)
    return out, 200

def handle_add_feed(user_id: str, url: str):
    if user_id not in calendar_manager.users:
        return {"error": "User not found"}, 404
    if not url.strip():
        return {"error": "URL cannot be empty"}, 400
    added = calendar_manager.add_user_calendar_link(user_id, url.strip())
    return {
        "success": True,
        "calendar_urls": calendar_manager.users[user_id].calendar_urls,
        "event_count": len(calendar_manager.user_events.get(user_id, []))
    }, 200

def handle_sync_all():
    calendar_manager.refresh_all_calendars()
    return {
        "success": True,
        "last_sync": calendar_manager.last_sync_time,
        "user_counts": {uid: len(evs) for uid, evs in calendar_manager.user_events.items()}
    }, 200

def handle_get_posts():
    return [p.to_dict() for p in calendar_manager.posts], 200

def handle_create_post(data: Dict[str, Any]):
    author_id = data.get("author_id", "alice")
    author = calendar_manager.users.get(author_id)
    if not author:
        return {"error": "Author not found"}, 404

    is_verified = bool(data.get("is_verified_event", False))
    post_id = f"post-{uuid.uuid4().hex[:8]}"
    now_str = datetime.now(user_tz).isoformat()

    post = SocialPost(
        id=post_id,
        author_id=author_id,
        author_name=author.name,
        author_handle=author.handle,
        author_avatar=author.avatar,
        is_verified_event=is_verified,
        event_uid=data.get("event_uid"),
        event_summary=data.get("event_summary", "Calendar Moment"),
        event_start=data.get("event_start"),
        event_end=data.get("event_end"),
        event_location=data.get("event_location", ""),
        event_provider=data.get("event_provider", "Manual"),
        photo_url=data.get("photo_url", "/static/images/coffee_photo.svg"),
        caption=data.get("caption", ""),
        created_at=now_str,
        privacy=data.get("privacy", "public"),
        likes=0
    )
    calendar_manager.add_post(post)
    return post.to_dict(), 201

def handle_like_post(post_id: str):
    likes = calendar_manager.like_post(post_id)
    return {"post_id": post_id, "likes": likes}, 200

def handle_availability_compare(data: Dict[str, Any]):
    date_str = data.get("date", datetime.now(user_tz).strftime("%Y-%m-%d"))
    participant_ids = data.get("participants", list(calendar_manager.users.keys()))
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format, expected YYYY-MM-DD"}, 400

    result = compute_group_availability(
        target_date=target_date,
        users=calendar_manager.users,
        events_by_user=calendar_manager.user_events,
        participant_ids=participant_ids,
        user_tz=user_tz
    )
    return result.to_dict(), 200

def handle_preflight_check(data: Dict[str, Any]):
    date_str = data.get("date", datetime.now(user_tz).strftime("%Y-%m-%d"))
    start_time = data.get("start_time", "14:00")
    end_time = data.get("end_time", "15:00")
    participant_ids = data.get("participants", [])

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format, expected YYYY-MM-DD"}, 400

    result = check_preflight_conflicts(
        target_date=target_date,
        start_time_str=start_time,
        end_time_str=end_time,
        participant_ids=participant_ids,
        events_by_user=calendar_manager.user_events,
        users=calendar_manager.users,
        user_tz=user_tz
    )
    return result.to_dict(), 200

def handle_create_schedule(data: Dict[str, Any]):
    title = data.get("title", "New Group Event")
    date_str = data.get("date", datetime.now(user_tz).strftime("%Y-%m-%d"))
    start_time_str = data.get("start_time", "15:00")
    end_time_str = data.get("end_time", "16:00")
    location = data.get("location", "")
    description = data.get("description", "")
    participants = data.get("participants", [])
    organizer_id = data.get("organizer_id", "alice")

    if organizer_id not in participants:
        participants.append(organizer_id)

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        s_h, s_m = [int(p) for p in start_time_str.split(":")]
        e_h, e_m = [int(p) for p in end_time_str.split(":")]
        start_dt = datetime.combine(target_date, time(s_h, s_m), tzinfo=user_tz)
        end_dt = datetime.combine(target_date, time(e_h, e_m), tzinfo=user_tz)
    except Exception as e:
        return {"error": f"Invalid date or time: {e}"}, 400

    event_uid = f"social-event-{uuid.uuid4().hex[:8]}"

    # Commit event to each participant's local store
    committed_to = []
    for uid in participants:
        if uid in calendar_manager.users:
            save_event_to_local_store(
                user_id=uid,
                uid=event_uid,
                title=title,
                start_dt=start_dt,
                end_dt=end_dt,
                location=location,
                description=description,
                attendees=participants
            )
            calendar_manager.refresh_user_calendar(uid)
            committed_to.append(uid)

    ics_content = generate_ics_invite(
        uid=event_uid,
        title=title,
        start_dt=start_dt,
        end_dt=end_dt,
        location=location,
        description=description,
        attendees=participants
    )

    return {
        "success": True,
        "event_uid": event_uid,
        "title": title,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "participants": committed_to,
        "ics_content": ics_content
    }, 201

def handle_discord_inbound(data: Dict[str, Any]):
    sender_id = data.get("sender_id") or data.get("author_id") or data.get("discord_id") or data.get("from") or "alice#1337"
    content = data.get("content") or data.get("message") or data.get("body") or ""
    attachment_url = data.get("attachment_url") or data.get("media_url") or None
    channel = data.get("channel") or DISCORD_DEFAULT_CHANNEL

    # Resolve sender profile for author metadata
    user = find_user_by_discord(sender_id)
    if user:
        author_meta = {
            "id": user.discord_id or sender_id,
            "username": user.discord_username or user.handle,
            "name": user.name,
            "avatar": user.avatar,
            "bot": False
        }
    else:
        author_meta = {
            "id": sender_id,
            "username": sender_id,
            "name": sender_id,
            "avatar": "👤",
            "bot": False
        }

    reply_text, embed, meta = handle_incoming_discord_message(
        sender_identifier=sender_id,
        content=content,
        attachment_url=attachment_url,
        channel=channel
    )

    t_str = datetime.now(user_tz).strftime("%I:%M %p")
    user_msg_id = f"msg-{uuid.uuid4().hex[:8]}"
    discord_logs.append({
        "id": user_msg_id,
        "timestamp": t_str,
        "author": author_meta,
        "channel": channel,
        "content": content,
        "attachment_url": attachment_url,
        "embed": None
    })

    bot_msg_id = f"msg-{uuid.uuid4().hex[:8]}"
    discord_logs.append({
        "id": bot_msg_id,
        "timestamp": t_str,
        "author": {
            "id": DISCORD_BOT_ID,
            "username": "CalMedia Bot#0001",
            "name": DISCORD_BOT_NAME,
            "avatar": "🤖",
            "bot": True
        },
        "channel": channel,
        "content": reply_text,
        "attachment_url": None,
        "embed": embed
    })

    return {
        "reply": reply_text,
        "embed": embed,
        "meta": meta
    }, 200

# Lightweight HTTP Server implementation for Zero-Dependency Execution
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class SocialCalendarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Serve Frontend HTML
        if path == "/" or path == "/index.html":
            html_file = settings.BASE_DIR / "app" / "templates" / "index.html"
            content = html_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # Serve Static CSS / JS / Images
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            static_file = settings.BASE_DIR / "app" / "static" / rel_path
            if static_file.exists() and static_file.is_file():
                mime, _ = mimetypes.guess_type(str(static_file))
                content = static_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, "Static file not found")
                return

        # Serve Uploads
        if path.startswith("/uploads/"):
            rel_path = path[len("/uploads/"):]
            upload_file = settings.UPLOAD_DIR / rel_path
            if upload_file.exists() and upload_file.is_file():
                mime, _ = mimetypes.guess_type(str(upload_file))
                content = upload_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # API Endpoints
        if path == "/api/users":
            res = handle_get_users()
            self._send_json(res)
            return
        elif path.startswith("/api/users/") and path.endswith("/network"):
            uid = path.split("/")[3]
            res, code = handle_get_network(uid)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/events"):
            parts = path.split("/")
            uid = parts[3]
            viewer = query.get("viewer", [""])[0]
            res, code = handle_get_user_events(uid, viewer)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/"):
            uid = path.split("/")[3]
            res, code = handle_get_user(uid)
            self._send_json(res, code)
            return
        elif path == "/api/posts":
            res, code = handle_get_posts()
            self._send_json(res, code)
            return
        elif path == "/api/health":
            self._send_json({"status": "healthy", "service": "Calendar Social Media Harness", "port": settings.PORT})
            return
        elif path == "/api/discord/logs":
            self._send_json(discord_logs)
            return
        elif path == "/api/discord/bot-info":
            self._send_json({
                "bot_name": DISCORD_BOT_NAME,
                "bot_id": DISCORD_BOT_ID,
                "default_channel": DISCORD_DEFAULT_CHANNEL,
                "linked_accounts": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "handle": u.handle,
                        "discord_username": u.discord_username,
                        "discord_id": u.discord_id
                    }
                    for u in calendar_manager.users.values()
                ]
            })
            return

        self.send_error(404, "Path not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        content_type = self.headers.get("Content-Type", "")
        if "application/x-www-form-urlencoded" in content_type:
            parsed_form = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"))
            data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed_form.items()}
        else:
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                data = {}

        if path == "/api/sync":
            res, code = handle_sync_all()
            self._send_json(res, code)
            return
        elif path == "/api/users":
            res, code = handle_create_user(data)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/connect"):
            uid = path.split("/")[3]
            res, code = handle_connect_friend(uid, data)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/accept-friend"):
            uid = path.split("/")[3]
            res, code = handle_accept_friend(uid, data)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/decline-friend"):
            uid = path.split("/")[3]
            res, code = handle_decline_friend(uid, data)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/unfriend"):
            uid = path.split("/")[3]
            res, code = handle_unfriend(uid, data)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/privacy"):
            uid = path.split("/")[3]
            res, code = handle_toggle_privacy(uid)
            self._send_json(res, code)
            return
        elif path.startswith("/api/users/") and path.endswith("/feeds"):
            uid = path.split("/")[3]
            url = data.get("url", "")
            res, code = handle_add_feed(uid, url)
            self._send_json(res, code)
            return
        elif path == "/api/posts":
            res, code = handle_create_post(data)
            self._send_json(res, code)
            return
        elif path.startswith("/api/posts/") and path.endswith("/like"):
            post_id = path.split("/")[3]
            res, code = handle_like_post(post_id)
            self._send_json(res, code)
            return
        elif path == "/api/availability/compare":
            res, code = handle_availability_compare(data)
            self._send_json(res, code)
            return
        elif path == "/api/schedule/preflight":
            res, code = handle_preflight_check(data)
            self._send_json(res, code)
            return
        elif path == "/api/schedule/create":
            res, code = handle_create_schedule(data)
            self._send_json(res, code)
            return
        elif path == "/api/discord/webhook":
            res, code = handle_discord_inbound(data)
            self._send_json(res, code)
            return
        elif path == "/api/discord/simulate":
            res, code = handle_discord_inbound(data)
            self._send_json(res, code)
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, payload: Any, status: int = 200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

def run_server(port: int = None, host: str = None):
    p = port or settings.PORT
    h = host or settings.HOST
    server_address = (h, p)
    httpd = HTTPServer(server_address, SocialCalendarHandler)
    print(f"================================================================")
    print(f" Calendar Social Media Test Harness listening on http://localhost:{p}")
    print(f" Default Personas: Alice Chen (@alice), Bob Martinez (@bob), Charlie Taylor (@charlie)")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()

