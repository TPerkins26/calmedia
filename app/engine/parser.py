import re
import uuid
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from typing import List, Optional, Union
from app.models import CalendarEvent

def parse_ics_datetime(dt_str: str, default_tz: ZoneInfo) -> datetime:
    """Parses standard RFC 5545 datetime or date string into a timezone-aware datetime."""
    dt_str = dt_str.strip()
    
    # Check for UTC 'Z' indicator
    if dt_str.endswith("Z"):
        clean_str = dt_str[:-1]
        dt = datetime.strptime(clean_str, "%Y%m%dT%H%M%S")
        return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(default_tz)
    
    # Check for datetime without Z: YYYYMMDDTHHMMSS
    if "T" in dt_str:
        clean_str = dt_str.split("T")[0] + "T" + dt_str.split("T")[1][:6]
        dt = datetime.strptime(clean_str, "%Y%m%dT%H%M%S")
        return dt.replace(tzinfo=default_tz)
    
    # Date only: YYYYMMDD
    if len(dt_str) >= 8:
        d = datetime.strptime(dt_str[:8], "%Y%m%d").date()
        return datetime.combine(d, time.min, tzinfo=default_tz)
    
    raise ValueError(f"Unrecognized datetime string: {dt_str}")

def parse_ics_content(
    ics_text: str,
    user_id: str,
    provider: str = "Imported",
    user_tz: Optional[ZoneInfo] = None,
    window_start: Optional[datetime] = None,
    window_end: Optional[datetime] = None
) -> List[CalendarEvent]:
    """
    Parses RFC 5545 .ics content into a list of normalized CalendarEvents.
    Expands weekly recurring events across the target time window.
    """
    if not user_tz:
        user_tz = ZoneInfo("America/New_York")
    
    now = datetime.now(user_tz)
    if not window_start:
        window_start = now - timedelta(days=30)
    if not window_end:
        window_end = now + timedelta(days=30)

    events: List[CalendarEvent] = []
    
    # Clean up line unfoldings (RFC 5545: lines beginning with whitespace continue previous line)
    unfolded_lines: List[str] = []
    for raw_line in ics_text.splitlines():
        if (raw_line.startswith(" ") or raw_line.startswith("\t")) and unfolded_lines:
            unfolded_lines[-1] += raw_line[1:]
        else:
            unfolded_lines.append(raw_line)

    in_vevent = False
    current_data = {}

    day_code_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

    for line in unfolded_lines:
        line = line.strip()
        if line == "BEGIN:VEVENT":
            in_vevent = True
            current_data = {}
            continue
        elif line == "END:VEVENT":
            in_vevent = False
            if "DTSTART" not in current_data:
                continue

            summary = current_data.get("SUMMARY", "Untitled Event")
            uid = current_data.get("UID", str(uuid.uuid4()))
            location = current_data.get("LOCATION", "")
            description = current_data.get("DESCRIPTION", "")
            rrule = current_data.get("RRULE", "")

            try:
                base_start = parse_ics_datetime(current_data["DTSTART"], user_tz)
            except Exception:
                continue

            if "DTEND" in current_data:
                try:
                    base_end = parse_ics_datetime(current_data["DTEND"], user_tz)
                except Exception:
                    base_end = base_start + timedelta(hours=1)
            else:
                base_end = base_start + timedelta(hours=1)

            event_duration = base_end - base_start
            if event_duration.total_seconds() <= 0:
                event_duration = timedelta(hours=1)

            # Expand weekly recurrence if present
            if rrule and "FREQ=WEEKLY" in rrule.upper():
                bydays = []
                byday_match = re.search(r"BYDAY=([A-Z,]+)", rrule.upper())
                if byday_match:
                    bydays = [d.strip() for d in byday_match.group(1).split(",")]
                
                target_days = [day_code_map[d] for d in bydays if d in day_code_map]
                if not target_days:
                    target_days = [base_start.weekday()]

                cur_day = window_start.date()
                end_day = window_end.date()

                while cur_day <= end_day:
                    if cur_day.weekday() in target_days:
                        occ_start = datetime.combine(cur_day, base_start.time(), tzinfo=user_tz)
                        occ_end = occ_start + event_duration
                        if window_start <= occ_end and occ_start <= window_end:
                            events.append(CalendarEvent(
                                uid=f"{uid}-{cur_day.isoformat()}",
                                summary=summary,
                                start=occ_start,
                                end=occ_end,
                                location=location,
                                description=description,
                                provider=provider,
                                is_all_day=False,
                                user_id=user_id
                            ))
                    cur_day += timedelta(days=1)
            else:
                # Single non-recurring event
                if window_start <= base_end and base_start <= window_end:
                    events.append(CalendarEvent(
                        uid=uid,
                        summary=summary,
                        start=base_start,
                        end=base_end,
                        location=location,
                        description=description,
                        provider=provider,
                        is_all_day=False,
                        user_id=user_id
                    ))
        elif in_vevent and ":" in line:
            parts = line.split(":", 1)
            prop_key = parts[0].split(";")[0].upper()
            prop_val = parts[1]
            current_data[prop_key] = prop_val

    # Sort chronologically
    events.sort(key=lambda e: e.start)
    return events

