from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional, Tuple
from app.models import CalendarEvent, UserProfile, FreeSlot, GroupAvailabilityResult, PreflightCheckResult

def merge_intervals(intervals: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    """Merges overlapping or contiguous time intervals."""
    if not intervals:
        return []
    sorted_inv = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_inv[0]]
    for cur_start, cur_end in sorted_inv[1:]:
        prev_start, prev_end = merged[-1]
        if cur_start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, cur_end))
        else:
            merged.append((cur_start, cur_end))
    return merged

def compute_group_availability(
    target_date: date,
    users: Dict[str, UserProfile],
    events_by_user: Dict[str, List[CalendarEvent]],
    participant_ids: List[str],
    user_tz: ZoneInfo,
    day_start_hour: int = 8,
    day_end_hour: int = 22,
    min_slot_minutes: int = 30
) -> GroupAvailabilityResult:
    """
    Computes mutual free time slots and per-user busy intervals across a group of participants.
    Applies privacy masking if user.privacy_mode == 'busy_only'.
    """
    window_start = datetime.combine(target_date, time(day_start_hour, 0), tzinfo=user_tz)
    window_end = datetime.combine(target_date, time(day_end_hour, 0), tzinfo=user_tz)

    user_busy_intervals: Dict[str, List[Dict[str, Any]]] = {}
    user_free_intervals: Dict[str, List[Tuple[datetime, datetime]]] = {}
    total_conflicts = 0

    for uid in participant_ids:
        user_profile = users.get(uid)
        is_busy_only = user_profile.privacy_mode == "busy_only" if user_profile else False

        raw_events = events_by_user.get(uid, [])
        # Filter events active on target_date and within window
        day_events = [
            e for e in raw_events
            if e.end > window_start and e.start < window_end
        ]

        # Collect and merge busy spans for math
        busy_spans = []
        for e in day_events:
            span_start = max(e.start, window_start)
            span_end = min(e.end, window_end)
            if span_start < span_end:
                busy_spans.append((span_start, span_end))

        merged_busy = merge_intervals(busy_spans)

        # Build display list with privacy masking
        display_events = []
        for e in day_events:
            display_events.append({
                "uid": e.uid,
                "summary": "🔒 Busy" if is_busy_only else e.summary,
                "start": e.start.isoformat(),
                "end": e.end.isoformat(),
                "location": "" if is_busy_only else (e.location or ""),
                "provider": e.provider,
                "is_masked": is_busy_only
            })
        user_busy_intervals[uid] = display_events

        # Calculate user's free intervals within window
        free_spans: List[Tuple[datetime, datetime]] = []
        cur_pointer = window_start
        for b_start, b_end in merged_busy:
            if b_start > cur_pointer:
                free_spans.append((cur_pointer, b_start))
            cur_pointer = max(cur_pointer, b_end)
        if cur_pointer < window_end:
            free_spans.append((cur_pointer, window_end))
        
        user_free_intervals[uid] = free_spans

    # Calculate set intersection of free intervals across all participants
    if not participant_ids:
        mutual_free_intervals = [(window_start, window_end)]
    else:
        # Start with the first participant's free spans
        current_intersect = user_free_intervals.get(participant_ids[0], [])
        for uid in participant_ids[1:]:
            next_free = user_free_intervals.get(uid, [])
            new_intersect = []
            for s1, e1 in current_intersect:
                for s2, e2 in next_free:
                    overlap_start = max(s1, s2)
                    overlap_end = min(e1, e2)
                    if overlap_end > overlap_start:
                        new_intersect.append((overlap_start, overlap_end))
            current_intersect = merge_intervals(new_intersect)
        mutual_free_intervals = current_intersect

    # Format free slots and filter by min_slot_minutes
    mutual_free_slots: List[FreeSlot] = []
    for s, e in mutual_free_intervals:
        duration_mins = int((e - s).total_seconds() / 60)
        if duration_mins >= min_slot_minutes:
            # Check social hours (lunch 11:30-13:30 or evening 17:00-21:00)
            is_social = (11 <= s.hour <= 13) or (17 <= s.hour <= 21)
            mutual_free_slots.append(FreeSlot(
                start=s.strftime("%H:%M"),
                end=e.strftime("%H:%M"),
                duration_minutes=duration_mins,
                is_social_hour=is_social
            ))

    return GroupAvailabilityResult(
        target_date=target_date.isoformat(),
        participants=participant_ids,
        mutual_free_slots=mutual_free_slots,
        user_busy_intervals=user_busy_intervals,
        conflicts_detected=total_conflicts
    )

def check_preflight_conflicts(
    target_date: date,
    start_time_str: str,
    end_time_str: str,
    participant_ids: List[str],
    events_by_user: Dict[str, List[CalendarEvent]],
    users: Dict[str, UserProfile],
    user_tz: ZoneInfo
) -> PreflightCheckResult:
    """
    Evaluates proposed meeting times against all participants' schedules.
    Returns conflicts detected and suggests mutual free alternatives.
    """
    s_hour, s_min = [int(p) for p in start_time_str.split(":")]
    e_hour, e_min = [int(p) for p in end_time_str.split(":")]
    prop_start = datetime.combine(target_date, time(s_hour, s_min), tzinfo=user_tz)
    prop_end = datetime.combine(target_date, time(e_hour, e_min), tzinfo=user_tz)

    conflicts = []
    for uid in participant_ids:
        user_obj = users.get(uid)
        user_name = user_obj.name if user_obj else uid
        for e in events_by_user.get(uid, []):
            if prop_start < e.end and prop_end > e.start:
                conflicts.append({
                    "user_id": uid,
                    "user_name": user_name,
                    "conflicting_event": "🔒 Busy" if (user_obj and user_obj.privacy_mode == "busy_only") else e.summary,
                    "start": e.start.strftime("%H:%M"),
                    "end": e.end.strftime("%H:%M")
                })

    # Compute alternative free slots on this day
    avail_res = compute_group_availability(
        target_date=target_date,
        users=users,
        events_by_user=events_by_user,
        participant_ids=participant_ids,
        user_tz=user_tz
    )

    return PreflightCheckResult(
        is_conflict_free=(len(conflicts) == 0),
        conflicts=conflicts,
        alternative_slots=avail_res.mutual_free_slots
    )

