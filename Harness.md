# Calendar Social Media Test Harness Specification

## Overview

The **Calendar Social Media Test Harness** (`TP_Project_2.1`) is an interactive MVP, social scheduling engine, and verification environment. Building upon the multi-provider calendar ingestion and deterministic scheduling engine of `TP_Project_2`, this system introduces a **calendar-centric social network**.

In this platform:
1. **Users import their schedules** via shareable calendar links (Google Calendar, Apple iCloud, Microsoft Outlook, Canvas LMS, and RFC 5545 `.ics` feeds).
2. **Users document and share real-world experiences** by attaching photos and captions directly to past or ongoing calendar events ("Calendar Moments" / "Proof of Life").
3. **Friends compare mutual availability** through an automated multi-schedule overlap and heatmap engine that calculates common free windows across groups.
4. **Groups coordinate and schedule shared events**, with real-time pre-flight conflict detection across all invitees' connected calendars.

The harness runs locally on `http://localhost:8081` with an interactive, responsive web GUI and a full suite of automated verification tests.

---

## 1. System Architecture & Tech Stack

* **Language**: Python 3.10+
* **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) with [Uvicorn](https://www.uvicorn.org/) ASGI server
* **Default Port**: `8081` (`http://localhost:8081` — distinct from `TP_Project_2` to allow concurrent side-by-side execution)
* **Calendar Parsing & Recurrence Expansion**: `icalendar` and `recurring_ical_events` (RFC 5545 compliant)
* **HTTP Client**: `httpx` (asynchronous feed retrieval and calendar synchronization)
* **Database & Persistence**: SQLite via lightweight ORM / Pydantic models for user profiles, friend connections, photo metadata, and social posts
* **Media Storage**: Local media upload pipeline (`data/uploads/`) with mime-type validation and thumbnail generation/serving
* **Frontend**: HTML5, CSS3, Modern Vanilla JavaScript (ES modules), and Jinja2 templates (no heavy JS framework build steps required)
* **Testing & Verification**: `pytest` and `httpx.AsyncClient` for automated unit and integration tests

---

## 2. Multi-User Ingestion & Shareable Calendar Feeds

The system shifts the ingestion model from single-user multi-provider aggregation to **multi-user social aggregation**:

### 2.1 Supported Shareable Calendar Formats
* **Google Calendar**: Secret or public iCal subscription URL (`https://calendar.google.com/calendar/ical/.../basic.ics`)
* **Apple iCloud**: Public or shared webcal subscription link (`webcal://...` or `https://.../calendar.ics`)
* **Microsoft Outlook 365**: Published ICS calendar link (`https://outlook.office365.com/owa/calendar/.../reachcalendar.ics`)
* **Canvas LMS & Academic Portals**: Student/course calendar feed URL (`https://canvas.../feeds/calendars/...ics`)
* **Raw iCal Files**: Ad-hoc upload of `.ics` files for testing and offline scenarios.

### 2.2 Feed Synchronization & Caching
* **Background Sync Service**:
  * Periodically polls all registered user calendar links in the background.
  * Local cache layer (`data/cache/users/<user_id>/`) stores raw `.ics` payloads to guarantee offline capability and rapid rendering.
  * Resilient error handling flags dead or malformed URLs without halting the background worker.
* **Seed & Demo Personas**:
  * Out-of-the-box demo profiles (e.g., Alice, Bob, Charlie) pre-populated with realistic academic and social calendar feeds, recurring classes, study blocks, and conflicting meetings.

---

## 3. Social Event Feed & Photo Journaling ("Calendar Moments")

A core differentiator of the platform is anchoring social media posts to **calendar events**, using a **Flexible Hybrid Model**:

### 3.1 Post Types & Data Model
* **Flexible Hybrid Creation**:
  1. **Verified Calendar Event Post**: Attached to an existing event parsed from the user's synced calendar feed. Displays a `📅 Verified Event: [Event Name]` badge.
  2. **Spontaneous Moment Post**: Allows the user to capture an unscheduled experience on the fly, creating a timestamped event card with a `⚡ Spontaneous Moment` badge.
* **Post Schema**:
  * **Post ID**: Unique identifier (UUID).
  * **Author**: User ID, display name, handle, and avatar.
  * **Calendar Event Reference**:
    * `is_verified_event`: Boolean flag indicating if it was ingested from an external calendar feed.
    * `event_uid`: RFC 5545 UID of the associated event (or generated UUID for spontaneous events).
    * `summary`: Event title (e.g., "Art History Field Trip", "CS Study Group", "Fall Concert").
    * `start_time` / `end_time`: Event timestamp window (normalized to ISO 8601 UTC).
    * `location`: Physical venue or virtual link.
    * `provider`: Calendar origin tag (Google, Apple, Outlook, Canvas, or Manual).
  * **Media Content**:
    * Uploaded image path(s) (`.png`, `.jpg`, `.jpeg`, `.webp`).
    * Caption text, hashtags, and attendee tags.
  * **Privacy Controls**:
    * `Public`: Visible across the global discovery feed.
    * `Friends Only`: Visible only to mutual friends.
    * `Private`: Personal journal entry attached to the user's private calendar view.

### 3.2 Feed Timeline
* Chronological visual feed showing event cards containing:
  * Event badge (`📅 Verified Event` vs `⚡ Spontaneous Moment`).
  * High-resolution photo preview.
  * Timestamp, location pill, and attendee chips.
  * Social engagement counters (reactions and comments).

---

## 4. Multi-Friend Availability Comparison Engine

A deterministic, non-AI algorithm that aggregates schedules across two or more users to identify mutual free time for social planning.

### 4.1 Timezone & Recurrence Normalization
* Expands all active `RRULE` recurrence patterns for each user's calendar over a target analysis window (e.g., Today, Next 7 Days, Selected Weekend).
* Normalizes all event timestamps to the viewer's local timezone.

### 4.2 Group Availability Matrix & Free Block Calculation
* **Interval Math**: Treats each user's busy events as a union of closed time intervals $[S_i, E_i]$.
* **Intersection Algorithm**:
  * Inverts each user's busy intervals within a defined social window (e.g., 8:00 AM – 10:00 PM) to produce their free intervals.
  * Computes the set intersection of free intervals across all selected participants:
    $$\text{Free}_{\text{Group}} = \bigcap_{u \in \text{Participants}} \text{Free}_u$$
* **Best Meet Slot Recommendations**:
  * Identifies contiguous mutual free blocks meeting a configurable minimum duration (e.g., $\ge 30$, $60$, or $120$ minutes).
  * Ranks open windows by social desirability (e.g., lunch hour, afternoon break, evening hangout).

### 4.3 Privacy & Masking Modes (User Toggle)
* Each user profile maintains a privacy preference setting:
  * **Full Transparency**: Mutual friends see event titles, locations, and details (e.g., "Math 2301 Lecture", "Dinner at West Green").
  * **Masked as Busy**: Blocks out the time interval as `🔒 Busy` without disclosing event names or locations, protecting personal privacy while preserving group scheduling math.

---

## 5. Collaborative Social Scheduling & Proposals

Enables frictionless group event creation once mutual free time is identified.

### 5.1 Social Proposal Workflow
1. **Initiate**: A user selects an open slot from the Availability Matrix and enters event details (Title, Location/Link, Description, Target Date & Time).
2. **Invite Participants**: Select one or more connected friends.
3. **Pre-Flight Group Conflict Check**:
   * Evaluates the proposed slot against *every* invitee's live synced calendar.
   * If any participant has a collision, the GUI highlights the exact conflict (e.g., *"Warning: Bob has 'Physics Lab' until 3:30 PM"*).
   * Recommends the nearest unconflicted alternate slot.
4. **Dispatch & Persistence**:
   * Writes the event to each participant's **Local Mock ICS Store** (`data/local_store/<user_id>.ics`).
   * Generates a downloadable standard RFC 5545 `.ics` calendar invitation file.
   * Updates participants' timelines and availability immediately without requiring third-party OAuth production credentials.

---

## 6. Discord Bot & Gateway Integration (Action Webhooks)

Enables users to perform core social and calendar actions remotely using Discord bot commands (`!agenda`, `!free`, `!meet`, `!privacy`) and attachments in the designated channel (`#calendar-sync`).

### 6.1 Discord Protocol & Gateway Webhook
* **Endpoint**: `POST /api/discord/webhook`
* **Supported Payloads**: Standard JSON containing:
  * `sender_id`: Discord tag (e.g. `alice#1337`), Discord user ID, or handle.
  * `content`: Text message command or caption (prefixed with `!` or `/`).
  * `attachment_url` (Optional): Image attachment URL.
  * `channel` (Optional): Discord channel tag (default `#calendar-sync`).
* **Response**: Rich JSON payload with `reply` text and Discord-formatted `embed` (`title`, `description`, `color`, `fields`, `footer`, `image`).

### 6.2 Supported Inbound Actions
1. **Photo Moment Attachments**:
   * Attaching an image anchors it to the user's ongoing or most recent verified calendar event and publishes it to the Moments Feed.
2. **On-Demand Agenda Lookup**:
   * Command: `!agenda [date]` or `/agenda`
   * Returns formatted agenda list of meetings and classes with a Discord Blurple rich embed.
3. **Mutual Free Time Lookup**:
   * Command: `!free [@friend/ALL] [date]`
   * Calculates set intersection $\bigcap \text{Free}_u$ and renders open slots with 🔥 Prime tags.
4. **Direct Social Scheduling**:
   * Command: `!meet @friend HH:MM-HH:MM Title`
   * Performs real-time pre-flight conflict checking, generates Discord Yellow collision alert if blocked, or books directly into both participants' `.ics` local stores.
5. **Privacy Mode Control**:
   * Command: `!privacy [BUSY/OPEN]`
   * Toggles event masking.

---

## 7. Web GUI Requirements (`http://localhost:8081` & GitHub Pages)

The frontend delivers a unified dashboard with six primary views:

1. **Header & Navigation Bar**:
   * User Switcher (instantly switch between demo profiles like Alice, Bob, Charlie, and new user profiles).
   * **`✨ + Create Account` Button**: Launches the registration modal to create and immediately activate a new student profile.
   * Background sync indicator and "Sync Now" trigger.
   * Unread notification badge on the Campus Network & Friends tab for pending friend requests.
2. **Social Feed Tab**:
   * Feed of "Calendar Moments": cards displaying photos attached to real calendar events with author details and event metadata.
   * "Add Photo to Event" trigger: allows the active user to pick one of their recent calendar events and attach photos with a caption.
3. **Availability Comparison & Heatmap Tab**:
   * Multi-friend selector (checkboxes to pick who to compare against).
   * Time range selector (Today, Tomorrow, This Weekend, Next 7 Days).
   * Visual Heatmap / Grid: Time on the Y-axis, days/friends on the X-axis.
   * Highlighted "Mutual Free Time" slots with a 1-click **"Schedule Together"** action.
4. **Campus Network & Friends Tab (`#friends`)**:
   * **Incoming Requests**: Alerts and action buttons (Accept / Decline) for received friend connection requests.
   * **Mutual Friends**: Shows mutual friends, their privacy mode, synced event counts, with 1-click **Compare Free Time**, **Schedule Hangout**, **Discord Bot Coordination**, and **Unfriend**.
   * **Campus Student Directory**: Real-time search filter and "+ Connect" buttons for discovering classmates.
5. **My Calendar & Ingestion Manager Tab**:
   * List of connected shareable calendar feeds (Google, Apple, Outlook, Canvas) with status badges and event counts.
   * Form to paste new shareable `.ics` or `webcal://` links.
   * Ad-hoc `.ics` file drag-and-drop upload.
6. **Interactive Discord Bot Console Tab**:
   * Built-in Discord channel interface (`#calendar-sync`) allowing users to test chat commands and photo attachments as any linked Discord persona.
   * Displays authentic Discord dark-themed chat stream with author badges, `BOT` pills, rich embeds, and quick command chips.
7. **Interactive Modals**:
   * **Account Creation Modal**: Register profile name, handle (`@handle`), emoji avatar picker, bio, Discord tag, calendar link, and privacy mode.
   * **Photo Post Modal**: Choose event from recent schedule, upload image, write caption, choose privacy.
   * **Schedule Together Modal**: Date, time, title, pre-flight conflict indicator with live status tags.

---

## 8. GitHub Pages Deployment Specification (`site/`)

CalMedia includes a zero-backend static deployment bundle located in `TP_Project_2.1/site/` designed for GitHub Pages:

* **Live URL**: `https://thomasperkins.github.io/calmedia/social.html#friends` (documented in `link.md`).
* **Standalone Execution Engine**:
  * Employs an in-browser `localStorage` mock router that intercepts API calls when hosted statically.
  * Seeded with 5 distinct student profiles (Alice Chen, Bob Martinez, Charlie Taylor, Dana Scott, Evan Wright).
  * Executes mathematical interval intersection for mutual free times ($08:00 - 22:00$) entirely in client-side JavaScript.
  * Supports full friend request lifecycle (connect, reciprocal auto-accept, decline, unfriend), account registration, and Discord bot command simulation offline or serverless.

---

## 9. Verification & Acceptance Criteria

1. **Port & Server Startup**: Application boots on `0.0.0.0:8081` and binds cleanly without port collisions.
2. **Account Creation**: Users can create a profile via `POST /api/users` and frontend modal, immediately populating the user switcher, network directory, and personal agenda.
3. **Networking Between Two People**: Full friend connection lifecycle verified: sending request, receiving incoming alert, reciprocal auto-acceptance, and unfriend capability.
4. **Multi-User Link Ingestion**: Successfully downloads, caches, and parses `.ics` feeds for multiple independent user profiles.
5. **Photo Attachment & Social Feed**:
   * Successfully attaches an uploaded image to a verified calendar event UID.
   * Renders the post with valid metadata in the social feed.
   * Rejects invalid media file types or orphaned event UIDs.
6. **Deterministic Availability Intersect**:
   * Test suite verifies mathematical accuracy of mutual free time blocks when comparing 2, 3, or more users with overlapping busy schedules.
7. **Group Pre-Flight Collision Validation**:
   * Proposing an event during an invitee's busy window triggers a detectable conflict warning and suggests available alternatives.
8. **Inbound Discord Webhook & Command Execution**:
   * Inbound messages from registered Discord accounts trigger matching actions (`!agenda`, `!free`, `!meet`, `!privacy`).
   * Image attachments with captions publish moments directly to the feed.
   * Conflicting meetups trigger warning embeds with alternate open slots.
9. **Persona Switching & State Isolation**:
   * Switching between users in the GUI or API properly restricts private events and shows appropriate friend views.
10. **GitHub Pages Client-Side Parity**:
    * `site/index.html` and `site/social.html` operate standalone with zero backend dependencies, passing all in-browser harness scenarios.

