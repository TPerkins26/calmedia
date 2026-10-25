from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class CalendarEvent:
    uid: str
    summary: str
    start: datetime
    end: datetime
    location: Optional[str] = ""
    description: Optional[str] = ""
    provider: str = "Imported"
    is_all_day: bool = False
    user_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "summary": self.summary,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "location": self.location or "",
            "description": self.description or "",
            "provider": self.provider,
            "is_all_day": self.is_all_day,
            "user_id": self.user_id,
        }

@dataclass
class UserProfile:
    id: str
    name: str
    handle: str
    avatar: str
    bio: str = ""
    calendar_urls: List[str] = field(default_factory=list)
    privacy_mode: str = "transparent"  # "transparent" or "busy_only"
    friends: List[str] = field(default_factory=list)
    incoming_requests: List[str] = field(default_factory=list)
    outgoing_requests: List[str] = field(default_factory=list)
    discord_username: str = ""
    discord_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "handle": self.handle,
            "avatar": self.avatar,
            "bio": self.bio,
            "calendar_urls": self.calendar_urls,
            "privacy_mode": self.privacy_mode,
            "friends": self.friends,
            "incoming_requests": self.incoming_requests,
            "outgoing_requests": self.outgoing_requests,
            "discord_username": self.discord_username,
            "discord_id": self.discord_id,
        }

@dataclass
class SocialPost:
    id: str
    author_id: str
    author_name: str
    author_handle: str
    author_avatar: str
    is_verified_event: bool
    event_summary: str
    photo_url: str
    caption: str
    created_at: str
    event_uid: Optional[str] = None
    event_start: Optional[str] = None
    event_end: Optional[str] = None
    event_location: Optional[str] = None
    event_provider: Optional[str] = None
    privacy: str = "public"
    likes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class FreeSlot:
    start: str
    end: str
    duration_minutes: int
    is_social_hour: bool = False  # E.g. Lunch (11:30-13:30) or Evening (17:00-21:00)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GroupAvailabilityResult:
    target_date: str
    participants: List[str]
    mutual_free_slots: List[FreeSlot]
    user_busy_intervals: Dict[str, List[Dict[str, Any]]]
    conflicts_detected: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_date": self.target_date,
            "participants": self.participants,
            "mutual_free_slots": [s.to_dict() for s in self.mutual_free_slots],
            "user_busy_intervals": self.user_busy_intervals,
            "conflicts_detected": self.conflicts_detected,
        }

@dataclass
class PreflightCheckResult:
    is_conflict_free: bool
    conflicts: List[Dict[str, Any]]
    alternative_slots: List[FreeSlot]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_conflict_free": self.is_conflict_free,
            "conflicts": self.conflicts,
            "alternative_slots": [s.to_dict() for s in self.alternative_slots],
        }

