import re
import uuid
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Tuple, Dict, Any, List

from app.config import settings
from app.models import UserProfile, SocialPost
from app.ingestion.sync_service import calendar_manager
from app.engine.availability import compute_group_availability, check_preflight_conflicts
from app.writers.local_writer import save_event_to_local_store

# Standard Discord Colors
COLOR_BLURPLE = 0x5865F2
COLOR_GREEN = 0x57F287
COLOR_YELLOW = 0xFEE75C
COLOR_RED = 0xED4245

def clean_discord_handle(raw: str) -> str:
    """Cleans a Discord handle or mention (e.g. <@123456>, @alice, alice#1337)."""
    if not raw:
        return ""
    cleaned = raw.strip()
    # Strip Discord mention formatting <@!123456> or <@123456>
    if cleaned.startswith("<@") and cleaned.endswith(">"):
        cleaned = re.sub(r"[<@!>]", "", cleaned)
    return cleaned

def find_user_by_discord(identifier: str) -> Optional[UserProfile]:
    """
    Looks up registered UserProfile by Discord ID, Discord username/tag (e.g. alice#1337),
    or handle/name (e.g. @alice, alice).
    """
    if not identifier:
        return None
    raw = clean_discord_handle(identifier).lower()
    
    for user in calendar_manager.users.values():
        # Match Discord ID
        if user.discord_id and user.discord_id.lower() == raw:
            return user
        # Match full Discord username/tag (e.g. alice#1337)
        if user.discord_username and user.discord_username.lower() == raw:
            return user
        # Match username prefix before '#' (e.g. 'alice' matches 'alice#1337')
        if user.discord_username and user.discord_username.lower().split("#")[0] == raw:
            return user
        # Match user id or handle
        if user.id.lower() == raw or user.handle.lower().replace("@", "") == raw or user.handle.lower() == raw:
            return user
        # Match display name
        if user.name.lower() == raw:
            return user

    return None

def extract_target_date(text: str, default_date: date) -> date:
    """Extracts date from text (YYYY-MM-DD, TOMORROW, FRIDAY, etc.) or returns default_date."""
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            pass
    upper = text.upper()
    if "TOMORROW" in upper:
        return default_date + timedelta(days=1)
    if "YESTERDAY" in upper:
        return default_date - timedelta(days=1)
    day_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    for idx, day_name in enumerate(day_names):
        if day_name in upper:
            days_ahead = (idx - default_date.weekday()) % 7
            if days_ahead == 0 and "NEXT" in upper:
                days_ahead = 7
            return default_date + timedelta(days=days_ahead)
    return default_date

def handle_incoming_discord_message(
    sender_identifier: str,
    content: str,
    attachment_url: Optional[str] = None,
    channel: str = "#calendar-sync"
) -> Tuple[str, Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Parses and executes an inbound Discord message or slash command.
    Returns (reply_text, discord_embed, action_metadata).
    """
    user_tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(user_tz)
    user = find_user_by_discord(sender_identifier)

    if not user:
        reply = (
            f"❌ Discord account `{sender_identifier}` is not connected to a CalMedia calendar profile. "
            "Please log into http://localhost:8081 to link your Discord account."
        )
        embed = {
            "title": "Unregistered Discord Account",
            "description": f"No CalMedia profile found linked to `{sender_identifier}`.",
            "color": COLOR_RED,
            "fields": [
                {"name": "How to Connect", "value": "Visit the CalMedia web interface at http://localhost:8081 to link your Discord account.", "inline": False}
            ],
            "footer": {"text": f"CalMedia Bot • {channel}"}
        }
        return reply, embed, {"status": "unregistered_sender", "sender": sender_identifier}

    clean_content = content.strip()

    # 1. Handle Photo Attachments (Creates Social Moments anchored to Calendar Events)
    if attachment_url:
        caption = clean_content if clean_content else "Moment shared from Discord 📸"
        events = calendar_manager.user_events.get(user.id, [])

        # Check if there is an ongoing or nearby event today
        anchored_event = None
        for ev in events:
            if ev.start.date() == now.date() and (ev.start <= now <= ev.end or abs((ev.start - now).total_seconds()) < 7200):
                anchored_event = ev
                break

        post_id = f"discord-{uuid.uuid4().hex[:8]}"
        if anchored_event:
            new_post = SocialPost(
                id=post_id,
                author_id=user.id,
                author_name=user.name,
                author_handle=user.handle,
                author_avatar=user.avatar,
                is_verified_event=True,
                event_uid=anchored_event.uid,
                event_summary=anchored_event.summary,
                event_start=anchored_event.start.isoformat(),
                event_end=anchored_event.end.isoformat(),
                event_location=anchored_event.location or "",
                event_provider=anchored_event.provider,
                photo_url=attachment_url,
                caption=caption,
                created_at=now.isoformat(),
                privacy="public"
            )
            reply = f"📸 Moment posted! Photo anchored to your verified calendar event: '{anchored_event.summary}'."
            embed = {
                "title": f"📸 Verified Moment: {anchored_event.summary}",
                "description": caption,
                "color": COLOR_GREEN,
                "fields": [
                    {"name": "Author", "value": f"{user.name} ({user.handle})", "inline": True},
                    {"name": "Calendar Event", "value": f"✓ Verified ({anchored_event.provider})", "inline": True},
                    {"name": "Location", "value": anchored_event.location or "Athens, OH", "inline": True}
                ],
                "image": {"url": attachment_url},
                "footer": {"text": f"CalMedia Bot • Posted to Campus Feed • {channel}"}
            }
        else:
            new_post = SocialPost(
                id=post_id,
                author_id=user.id,
                author_name=user.name,
                author_handle=user.handle,
                author_avatar=user.avatar,
                is_verified_event=False,
                event_summary="Spontaneous Moment via Discord",
                photo_url=attachment_url,
                caption=caption,
                created_at=now.isoformat(),
                privacy="public"
            )
            reply = f"⚡ Spontaneous moment posted! Your photo is now live on the CalMedia campus feed."
            embed = {
                "title": "⚡ Spontaneous Moment Shared",
                "description": caption,
                "color": COLOR_BLURPLE,
                "fields": [
                    {"name": "Author", "value": f"{user.name} ({user.handle})", "inline": True},
                    {"name": "Type", "value": "Spontaneous Campus Moment", "inline": True}
                ],
                "image": {"url": attachment_url},
                "footer": {"text": f"CalMedia Bot • Posted to Campus Feed • {channel}"}
            }

        calendar_manager.add_post(new_post)
        return reply, embed, {"status": "discord_moment_posted", "post_id": post_id, "is_verified": bool(anchored_event)}

    # 2. Command Processing (Supports !, /, or plain keyword prefix)
    cmd_raw = clean_content
    # Strip leading ! or /
    if cmd_raw.startswith("!") or cmd_raw.startswith("/"):
        cmd_raw = cmd_raw[1:].strip()

    cmd_upper = cmd_raw.upper()

    # HELP COMMAND
    if cmd_upper in ("HELP", "?", "COMMANDS"):
        reply = (
            "🤖 **CalMedia Discord Bot Commands**:\n"
            "• `!agenda [date]` — View your schedule & classes\n"
            "• `!free [@friend/all] [date]` — Find mutual free time\n"
            "• `!meet @friend HH:MM-HH:MM Title` — Schedule & sync directly to calendars\n"
            "• `!privacy [busy/open]` — Toggle schedule visibility masking\n"
            "• Attach any photo to instantly post a moment to the feed!"
        )
        embed = {
            "title": "🤖 CalMedia Discord Bot Guide",
            "description": "Collaborative calendar commands & social photo moments directly inside Discord.",
            "color": COLOR_BLURPLE,
            "fields": [
                {"name": "!agenda [date]", "value": "Display your imported calendar events for today or specified date.", "inline": False},
                {"name": "!free [@friend/all]", "value": "Compute conflict-free overlapping open windows with friends.", "inline": False},
                {"name": "!meet @friend HH:MM-HH:MM [title]", "value": "Check pre-flight conflicts and insert confirmed event into both calendars.", "inline": False},
                {"name": "!privacy [busy/open]", "value": "Toggle between transparent titles and masked '🔒 Busy' blocks.", "inline": False},
                {"name": "Photo Moments", "value": "Attach an image to create an event-anchored or spontaneous moment on the campus feed.", "inline": False}
            ],
            "footer": {"text": f"CalMedia Bot • {channel}"}
        }
        return reply, embed, {"action": "help"}

    # AGENDA / TODAY COMMAND
    if cmd_upper.startswith("AGENDA") or cmd_upper.startswith("TODAY") or cmd_upper.startswith("SCHEDULE"):
        events = calendar_manager.user_events.get(user.id, [])
        target_date = extract_target_date(clean_content, now.date())
        day_events = [e for e in events if e.start.date() == target_date]
        day_events.sort(key=lambda x: x.start)

        date_label = "Today" if target_date == now.date() else target_date.strftime("%A, %b %d")
        if not day_events:
            reply = f"📅 Hi {user.name}, your schedule is clear for {date_label}! No events on file."
            embed = {
                "title": f"📅 Agenda for {user.name} ({date_label})",
                "description": "✨ Your schedule is completely clear for this date! No busy blocks found.",
                "color": COLOR_BLURPLE,
                "footer": {"text": f"CalMedia Bot • {channel}"}
            }
        else:
            lines = [f"📅 **{date_label}'s Agenda for {user.name}** ({len(day_events)} events):"]
            embed_fields = []
            for e in day_events:
                t_str = f"{e.start.strftime('%I:%M %p').lstrip('0')} - {e.end.strftime('%I:%M %p').lstrip('0')}"
                lines.append(f"• `{t_str}`: **{e.summary}** ({e.location or e.provider})")
                embed_fields.append({
                    "name": t_str,
                    "value": f"**{e.summary}**\n📍 {e.location or 'No location'} • {e.provider}",
                    "inline": False
                })
            reply = "\n".join(lines)
            embed = {
                "title": f"📅 {date_label}'s Agenda: {user.name}",
                "description": f"Found **{len(day_events)} scheduled events** on your calendar.",
                "color": COLOR_BLURPLE,
                "fields": embed_fields,
                "footer": {"text": f"CalMedia Bot • {channel}"}
            }
        return reply, embed, {"action": "agenda", "event_count": len(day_events), "date": target_date.isoformat()}

    # PRIVACY TOGGLE COMMAND
    if cmd_upper.startswith("PRIVACY"):
        parts = cmd_upper.split()
        if len(parts) > 1 and parts[1] in ("BUSY", "MASK", "MASKED", "HIDE", "LOCK"):
            user.privacy_mode = "busy_only"
            reply = "🔒 Privacy mode set to **Masked (Busy)**. Friends will only see your busy blocks."
            desc = "Your event titles and locations are now masked as '🔒 Busy' for friends."
        elif len(parts) > 1 and parts[1] in ("OPEN", "TRANSPARENT", "PUBLIC", "SHOW", "CLEAR"):
            user.privacy_mode = "transparent"
            reply = "🔓 Privacy mode set to **Transparent**. Mutual friends can see your event titles."
            desc = "Friends can now view full event details on the shared availability heatmap."
        else:
            new_mode = calendar_manager.toggle_privacy_mode(user.id)
            reply = f"Privacy mode toggled to: **{new_mode.upper()}**."
            desc = f"Your current calendar privacy mode is now: **{new_mode}**."

        embed = {
            "title": "🔒 Calendar Privacy Setting Updated",
            "description": desc,
            "color": COLOR_BLURPLE,
            "fields": [
                {"name": "Account", "value": f"{user.name} ({user.handle})", "inline": True},
                {"name": "Current Mode", "value": f"`{user.privacy_mode}`", "inline": True}
            ],
            "footer": {"text": f"CalMedia Bot • {channel}"}
        }
        return reply, embed, {"action": "privacy", "new_mode": user.privacy_mode}

    # FREE / AVAILABILITY COMMAND
    if cmd_upper.startswith("FREE"):
        target_date = extract_target_date(clean_content, now.date())
        parts = clean_content.split()
        target_uids = []
        if len(parts) == 1 or "ALL" in cmd_upper:
            target_uids = list(calendar_manager.users.keys())
        else:
            target_uids = [user.id]
            for p in parts[1:]:
                clean_target = p.replace("@", "").lower()
                for uid in calendar_manager.users:
                    u_cand = calendar_manager.users[uid]
                    if clean_target in (uid, u_cand.name.lower(), u_cand.handle.lower().replace("@", ""), u_cand.discord_username.lower().split("#")[0]):
                        if uid not in target_uids:
                            target_uids.append(uid)

        if len(target_uids) <= 1:
            target_uids = [user.id] + [f for f in user.friends if f in calendar_manager.users]

        avail = compute_group_availability(
            target_date=target_date,
            users=calendar_manager.users,
            events_by_user=calendar_manager.user_events,
            participant_ids=target_uids,
            user_tz=user_tz
        )

        names = [calendar_manager.users[uid].name for uid in target_uids if uid in calendar_manager.users]
        names_str = ", ".join(names)
        date_label = "today" if target_date == now.date() else target_date.strftime("%A, %b %d")

        if not avail.mutual_free_slots:
            reply = f"⚡ No mutual free windows found for {date_label} for {names_str}."
            embed = {
                "title": f"⚡ Availability: {names_str}",
                "description": f"No overlapping free slots found for **{date_label}**.",
                "color": COLOR_YELLOW,
                "footer": {"text": f"CalMedia Bot • {channel}"}
            }
        else:
            lines = [f"✨ **Mutual Free Time for {names_str}** ({date_label}):"]
            fields = []
            for s in avail.mutual_free_slots[:4]:
                prime = " (🔥 Prime)" if s.is_social_hour else ""
                lines.append(f"• `{s.start} - {s.end}` ({s.duration_minutes}m){prime}")
                fields.append({
                    "name": f"{s.start} – {s.end}",
                    "value": f"{s.duration_minutes} mins free{prime}",
                    "inline": True
                })
            lines.append("To book: `!meet @friend HH:MM-HH:MM Title`")
            reply = "\n".join(lines)
            embed = {
                "title": f"✨ Mutual Availability ({date_label})",
                "description": f"Found **{len(avail.mutual_free_slots)} open windows** between **{names_str}**:",
                "color": COLOR_BLURPLE,
                "fields": fields,
                "footer": {"text": f"CalMedia Bot • To schedule: !meet @friend HH:MM-HH:MM [Title] • {channel}"}
            }
        return reply, embed, {"action": "free_query", "slots": len(avail.mutual_free_slots), "date": target_date.isoformat()}

    # MEET / SCHEDULE COMMAND
    if cmd_upper.startswith("MEET") or cmd_upper.startswith("SCHEDULE"):
        target_date = extract_target_date(clean_content, now.date())
        time_match = re.search(r"(\d{1,2}:\d{2})\s*[-–to ]+\s*(\d{1,2}:\d{2})", clean_content)
        if not time_match:
            reply = "❌ Invalid time format. Example: `!meet @bob 15:00-16:00 Coffee Break`"
            embed = {
                "title": "❌ Invalid Time Format",
                "description": "Please specify the meeting time range using `HH:MM-HH:MM`.",
                "color": COLOR_RED,
                "fields": [
                    {"name": "Example Command", "value": "`!meet @bob 15:00-16:00 Coffee Break`", "inline": False}
                ],
                "footer": {"text": f"CalMedia Bot • {channel}"}
            }
            return reply, embed, {"error": "invalid_time_format"}

        start_time_str = time_match.group(1)
        end_time_str = time_match.group(2)

        if len(start_time_str) == 4:
            start_time_str = "0" + start_time_str
        if len(end_time_str) == 4:
            end_time_str = "0" + end_time_str

        participants = [user.id]
        words = clean_content.split()
        for w in words:
            clean_word = clean_discord_handle(w)
            if clean_word.startswith("@"):
                clean_word = clean_word[1:]
            for uid, u in calendar_manager.users.items():
                if clean_word.lower() in (uid, u.handle.lower().replace("@", ""), u.discord_username.lower().split("#")[0]):
                    if uid not in participants:
                        participants.append(uid)

        if len(participants) == 1 and user.friends:
            participants.append(user.friends[0])

        after_time = clean_content[time_match.end():].strip()
        title = after_time if after_time else "Spontaneous Meetup via Discord"

        preflight = check_preflight_conflicts(
            target_date=target_date,
            start_time_str=start_time_str,
            end_time_str=end_time_str,
            participant_ids=participants,
            events_by_user=calendar_manager.user_events,
            users=calendar_manager.users,
            user_tz=user_tz
        )

        if not preflight.is_conflict_free:
            conflict = preflight.conflicts[0]
            alt = f" Nearest open slot: `{preflight.alternative_slots[0].start} - {preflight.alternative_slots[0].end}`" if preflight.alternative_slots else ""
            reply = (
                f"⚠️ Collision detected: **{conflict['user_name']}** has **'{conflict['conflicting_event']}'** "
                f"during {conflict['start']}–{conflict['end']}.{alt}"
            )
            embed = {
                "title": "⚠️ Scheduling Conflict Detected",
                "description": f"Cannot schedule **'{title}'** due to calendar overlap.",
                "color": COLOR_YELLOW,
                "fields": [
                    {"name": "Conflict", "value": f"**{conflict['user_name']}** has *{conflict['conflicting_event']}*", "inline": True},
                    {"name": "Busy Window", "value": f"`{conflict['start']} – {conflict['end']}`", "inline": True},
                    {"name": "Suggested Slot", "value": f"`{preflight.alternative_slots[0].start} – {preflight.alternative_slots[0].end}`" if preflight.alternative_slots else "None today", "inline": False}
                ],
                "footer": {"text": f"CalMedia Bot • Pre-flight Conflict Detection • {channel}"}
            }
            return reply, embed, {"action": "meet_conflict", "conflicts": preflight.conflicts}

        s_h, s_m = [int(p) for p in start_time_str.split(":")]
        e_h, e_m = [int(p) for p in end_time_str.split(":")]
        start_dt = datetime.combine(target_date, time(s_h, s_m), tzinfo=user_tz)
        end_dt = datetime.combine(target_date, time(e_h, e_m), tzinfo=user_tz)

        event_uid = f"discord-meet-{uuid.uuid4().hex[:8]}"
        for pid in participants:
            save_event_to_local_store(
                user_id=pid,
                uid=event_uid,
                title=title,
                start_dt=start_dt,
                end_dt=end_dt,
                location="Athens, OH",
                description=f"Scheduled via Discord by {user.name}",
                attendees=participants
            )
            calendar_manager.refresh_user_calendar(pid)

        partner_names = [calendar_manager.users[pid].name for pid in participants if pid != user.id]
        date_label = "Today" if target_date == now.date() else target_date.strftime("%b %d")
        reply = (
            f"✓ Confirmed & Added to Calendars!\n"
            f"📅 **'{title}'** with {', '.join(partner_names)}\n"
            f"🕒 {date_label} `{start_time_str} - {end_time_str}`"
        )
        embed = {
            "title": f"✅ Calendar Event Booked: {title}",
            "description": f"Successfully synchronized to the calendar stores of all attendees.",
            "color": COLOR_GREEN,
            "fields": [
                {"name": "Attendees", "value": ", ".join([calendar_manager.users[p].name for p in participants if p in calendar_manager.users]), "inline": True},
                {"name": "Date & Time", "value": f"{date_label} `{start_time_str} – {end_time_str}`", "inline": True},
                {"name": "Location", "value": "Athens, OH", "inline": True}
            ],
            "footer": {"text": f"CalMedia Bot • Synced to Local ICS Stores • {channel}"}
        }
        return reply, embed, {"action": "meet_scheduled", "uid": event_uid, "participants": participants}

    # Default fallback
    reply = (
        f"CalMedia Bot received: `{clean_content}`.\n"
        "Unrecognized command. Type `!help`, `!agenda`, `!free`, or `!meet`."
    )
    embed = {
        "title": "❓ Unrecognized Command",
        "description": f"Command `{clean_content}` was not understood.",
        "color": COLOR_BLURPLE,
        "fields": [
            {"name": "Quick Commands", "value": "`!agenda`, `!free @bob`, `!meet @bob 15:00-16:00 Title`, `!privacy`, `!help`", "inline": False}
        ],
        "footer": {"text": f"CalMedia Bot • {channel}"}
    }
    return reply, embed, {"action": "unknown"}

