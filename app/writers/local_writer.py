import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import List, Optional

from app.config import settings

def format_ics_datetime(dt: datetime) -> str:
    """Formats datetime to ICS RFC 5545 string."""
    return dt.strftime("%Y%m%dT%H%M%S")

def generate_ics_invite(
    uid: str,
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    location: Optional[str] = "",
    description: Optional[str] = "",
    attendees: Optional[List[str]] = None
) -> str:
    """Generates a complete RFC 5545 VCALENDAR string for an event."""
    attendee_lines = ""
    if attendees:
        for att in attendees:
            attendee_lines += f"ATTENDEE;CN={att}:mailto:{att}@example.edu\n"

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//HTC//Calendar Social Media Scheduler//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")}
DTSTART;TZID=America/New_York:{format_ics_datetime(start_dt)}
DTEND;TZID=America/New_York:{format_ics_datetime(end_dt)}
SUMMARY:{title}
LOCATION:{location or ""}
DESCRIPTION:{description or ""}
{attendee_lines}STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR
"""
    return ics_content

def save_event_to_local_store(
    user_id: str,
    uid: str,
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    location: Optional[str] = "",
    description: Optional[str] = "",
    attendees: Optional[List[str]] = None
) -> Path:
    """
    Appends the scheduled VEVENT to the user's local store .ics file.
    """
    local_store_file = settings.LOCAL_STORE_DIR / f"{user_id}.ics"
    
    vevent_str = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")}
DTSTART;TZID=America/New_York:{format_ics_datetime(start_dt)}
DTEND;TZID=America/New_York:{format_ics_datetime(end_dt)}
SUMMARY:{title}
LOCATION:{location or ""}
DESCRIPTION:{description or ""}
STATUS:CONFIRMED
END:VEVENT
"""

    if not local_store_file.exists():
        header = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//HTC//Calendar Social Media Local Store//EN
CALSCALE:GREGORIAN
X-WR-CALNAME:{user_id.capitalize()}'s Local Scheduled Store
{vevent_str}END:VCALENDAR
"""
        local_store_file.write_text(header, encoding="utf-8")
    else:
        existing = local_store_file.read_text(encoding="utf-8")
        if "END:VCALENDAR" in existing:
            updated = existing.replace("END:VCALENDAR", f"{vevent_str}END:VCALENDAR")
        else:
            updated = existing + "\n" + vevent_str
        local_store_file.write_text(updated, encoding="utf-8")

    return local_store_file

