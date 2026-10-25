# AI Prompt & Interaction Log

## Session 1: Project Conception & Harness Specification

* **Timestamp**: 2026-10-15T17:07:00-04:00
* **Project**: TP_Project_2.1 — Calendar-Based Social Media Test Harness
* **Author / Collaborator**: Thomas Perkins (`thoma`)
* **Agent**: Antigravity (Advanced Agentic Pair Programmer)

---

### 1. User Prompt Received

```text
Using TP_Project_2 as a general guide, make a harness for a calendar based social media. The program should import peoples calendar through respected sharable links. From there, people can post photos of what those events on their calendar look like and can compare availablity to schedule things together. Ask me questions to clarify.
Create additionally a AiLogs.md file to record prompting
```

---

### 2. Prompt Analysis & Architectural Mapping

The user is extending the foundational calendar aggregation, parsing, and scheduling mechanics developed in `TP_Project_2` into a novel **Calendar-Centric Social Network**.

#### Key Capabilities Identified:
1. **Multi-User Calendar Link Ingestion**:
   * Instead of a single user aggregating their own private calendars (Google, Apple, Outlook), users connect via shareable calendar URLs (`.ics`, `webcal://`, Google secret/public URLs, Outlook feeds, Canvas feeds).
   * Social accounts link to one or more remote feeds with background sync and offline caching.
2. **Visual Event Posts & Photo Moments**:
   * Users can attach photos to past or active events on their calendar ("what those events look like" / real-world proof of life).
   * Social feed displaying chronological or event-grouped photo cards, captions, and attendance badges.
3. **Group Availability Comparison Engine**:
   * Multi-calendar overlap algorithm comparing 2 or more users' calendars.
   * Visual availability matrix / heatmap identifying mutual free blocks and scheduling collisions.
4. **Collaborative Social Scheduling**:
   * Propose hangouts, study sessions, or events directly within identified mutual free windows.
   * Real-time pre-flight conflict check against all participants' linked calendars.
   * Push scheduled events back to participants' calendars (or local mock store).
5. **Interactive Web GUI & Verification Test Suite**:
   * Served on `http://localhost:8081`.
   * Fast, responsive interface for feed browsing, photo uploads, availability comparison, and event creation.
   * Comprehensive pytest test suite with sample multi-user calendar seeds and mock social graph.

---

### 3. Logged Actions Taken

1. **Workspace Inspection**: Analyzed `TP_Project_2` architecture, `harness.md`, `README.md`, sync services, parsers, and test suites.
2. **Artifact Creation**:
   * Initialized `TP_Project_2.1/AiLogs.md` to track user prompts, architectural decisions, and agent responses.
   * Created comprehensive specification in `TP_Project_2.1/Harness.md` mirroring the structure and rigor of `TP_Project_2/harness.md`.
3. **Logged Actions Taken**:
   * Analyzed `TP_Project_2` architecture, `harness.md`, `README.md`, sync services, parsers, and test suites.
   * Created initial `TP_Project_2.1/AiLogs.md` to maintain full prompt audit trail.
   * Authored complete test harness specification in `TP_Project_2.1/Harness.md` covering:
     1. Architecture & Tech Stack (FastAPI, Python 3.10+, Uvicorn on port 8081, SQLite, icalendar)
     2. Multi-user shareable calendar link ingestion & background caching
     3. Social event feed & photo journaling ("Calendar Moments")
     4. Deterministic multi-friend availability comparison & heatmap engine
     5. Collaborative social event scheduling & pre-flight group collision detection
     6. Web GUI requirements with 4 distinct dashboard views
     7. Verification and automated acceptance criteria
   * Formulated interactive clarification questions for Thomas to finalize implementation preferences.

---

### 4. Clarification Questions & User Responses

* **Recorded At**: 2026-10-15T17:11:02-04:00

1. **Event Attachment Policy for Photos**:
   * **User Decision**: *Flexible Hybrid* — Users can attach photos to verified calendar events from their synced feeds, or create a quick event card on the fly if an experience was not scheduled in advance.
2. **Schedule Privacy & Transparency Among Friends**:
   * **User Decision**: *User Toggle* — Each user profile has a privacy toggle allowing them to choose whether mutual friends see full event titles/locations or mask slots simply as "Busy".
3. **Event Scheduling Target / Write-Back**:
   * **User Decision**: *Local Mock ICS Store per User + Downloadable `.ics` Invite* — Completely self-contained and verifiable without requiring third-party OAuth production credentials.

---

### 5. Implementation Roadmap for TP_Project_2.1

* [x] **Specification**: Authored complete specification in `Harness.md` reflecting user choices.
* [x] **Core Data Layer & Models**: Created `app/models.py` for user profiles, calendar events, social posts, and availability math.
* [x] **Ingestion & Sync Service**: Built `app/ingestion/sync_service.py` and `app/engine/parser.py` supporting RFC 5545 `.ics` feeds, recurrence rules, and offline caching.
* [x] **Availability & Heatmap Engine**: Built `app/engine/availability.py` with deterministic set intersection $\bigcap \text{Free}_u$, social hour detection, and pre-flight collision warnings.
* [x] **Social & Photo Engine**: Implemented `app/engine/mock_data.py` with seed personas (Alice, Bob, Charlie), photo moments, and verified event badges.
* [x] **Local Store Writer**: Built `app/writers/local_writer.py` for local `.ics` store commits and RFC 5545 calendar invite exports.
* [x] **Web GUI & User Switcher**: Created responsive dark-mode web application on `http://localhost:8081` with persona switching, moments feed, availability heatmap, and preflight scheduling modal.
* [x] **Verification & Automated Tests**: Authored 11 unit and integration tests across `tests/test_ingestion.py`, `tests/test_availability.py`, and `tests/test_social.py`.

---

### 6. Verification & Test Execution Results

* **Execution Command**: `PYTHONPATH=. python3 -m unittest discover -s tests -v`
* **Result**:
  ```text
  test_group_availability_overlap (test_availability.TestAvailability.test_group_availability_overlap) ... ok
  test_preflight_conflict_detection (test_availability.TestAvailability.test_preflight_conflict_detection) ... ok
  test_preflight_conflict_free_slot (test_availability.TestAvailability.test_preflight_conflict_free_slot) ... ok
  test_privacy_masking_for_busy_only_user (test_availability.TestAvailability.test_privacy_masking_for_busy_only_user) ... ok
  test_add_calendar_feed (test_ingestion.TestIngestion.test_add_calendar_feed) ... ok
  test_multi_user_manager_initialization (test_ingestion.TestIngestion.test_multi_user_manager_initialization) ... ok
  test_parse_alice_calendar (test_ingestion.TestIngestion.test_parse_alice_calendar) ... ok
  test_parse_bob_calendar (test_ingestion.TestIngestion.test_parse_bob_calendar) ... ok
  test_create_verified_post (test_social.TestSocial.test_create_verified_post) ... ok
  test_like_post (test_social.TestSocial.test_like_post) ... ok
  test_local_write_and_ics_generation (test_social.TestSocial.test_local_write_and_ics_generation) ... ok

  
---

## Session 2: Inbound SMS / Telephony Integration Exploration

* **Timestamp**: 2026-10-20T15:05:50-04:00
* **User Request**:
  ```text
  is it possible to add a function where you can send a text message from your phone number to a dessignated phone number to preform some action ?
  ```
* **Architectural Assessment**:
  1. **Feasibility**: Fully supported and standard practice using an SMS Webhook pattern (e.g. Twilio, Telnyx, Plivo, or carrier email-to-SMS gateway).
  2. **Core Capabilities Enabled**:
     * **MMS Photo Posting**: Texting an image + caption directly to the designated number automatically anchors it to the active/upcoming calendar event and posts it to the social feed.
     * **SMS Availability Query**: Texting `FREE bob` or `FREE ALL` returns the group's mutual free blocks for today/tomorrow via SMS.
     * **Instant Hangout Scheduling**: Texting `SCHEDULE 3pm-4pm Coffee with @bob` triggers the pre-flight conflict check and writes to both participants' calendars.
     * **Privacy Control**: Texting `PRIVACY BUSY` or `PRIVACY OPEN` toggles calendar transparency.
     * **Today's Agenda**: Texting `AGENDA` texts back the user's upcoming classes/meetings.
  3. **Harness & Verification Strategy**:
     * Implement an inbound webhook endpoint (`POST /api/sms/webhook`) adhering to standard webhook payload specifications (`From`, `Body`, `MediaUrl0`).
     * Provide an **Interactive SMS Simulator** in the GUI so the functionality is 100% testable without requiring a live paid telephony contract or exposed public tunnel.
     * Include environment variable overrides (`TWILIO_ACCOUNT_SID`, `TWILIO_PHONE_NUMBER`) for connecting to a live phone number when desired.




* **User Confirmation**: "sure" (Proceeded with full implementation).
* **Implementation Steps**:
  1. Updated `app/models.py` to add `phone_number` to `UserProfile`.
  2. Assigned phone numbers to Alice, Bob, and Charlie, plus system designated number (`+15550192831`) in `app/engine/mock_data.py`.
  3. Created `app/engine/sms_router.py` to parse incoming SMS/MMS messages and route commands.
  4. Wired `POST /api/sms/webhook`, `POST /api/sms/simulate`, and `GET /api/sms/logs` in `app/main.py`.
  5. Built smartphone chat interface & SMS Simulator tab in `app/templates/index.html` and `app/static/js/app.js`.
  6. Added automated unit tests in `tests/test_sms.py`.

* **Verification & Test Execution Results**:
  ```text
  test_group_availability_overlap (test_availability.TestAvailability.test_group_availability_overlap) ... ok
  test_preflight_conflict_detection (test_availability.TestAvailability.test_preflight_conflict_detection) ... ok
  test_preflight_conflict_free_slot (test_availability.TestAvailability.test_preflight_conflict_free_slot) ... ok
  test_privacy_masking_for_busy_only_user (test_availability.TestAvailability.test_privacy_masking_for_busy_only_user) ... ok
  test_add_calendar_feed (test_ingestion.TestIngestion.test_add_calendar_feed) ... ok
  test_multi_user_manager_initialization (test_ingestion.TestIngestion.test_multi_user_manager_initialization) ... ok
  test_parse_alice_calendar (test_ingestion.TestIngestion.test_parse_alice_calendar) ... ok
  test_parse_bob_calendar (test_ingestion.TestIngestion.test_parse_bob_calendar) ... ok
  test_agenda_command (test_sms.TestSMSRouter.test_agenda_command) ... ok
  test_find_user_by_phone (test_sms.TestSMSRouter.test_find_user_by_phone) ... ok
  test_free_availability_command (test_sms.TestSMSRouter.test_free_availability_command) ... ok
  test_meet_collision_detection (test_sms.TestSMSRouter.test_meet_collision_detection) ... ok
  test_meet_scheduling_command_success (test_sms.TestSMSRouter.test_meet_scheduling_command_success) ... ok
  test_mms_photo_moment (test_sms.TestSMSRouter.test_mms_photo_moment) ... ok
  test_privacy_command (test_sms.TestSMSRouter.test_privacy_command) ... ok
  test_twiml_generation (test_sms.TestSMSRouter.test_twiml_generation) ... ok
  test_unregistered_number (test_sms.TestSMSRouter.test_unregistered_number) ... ok
  test_create_verified_post (test_social.TestSocial.test_create_verified_post) ... ok
  test_like_post (test_social.TestSocial.test_like_post) ... ok
  test_local_write_and_ics_generation (test_social.TestSocial.test_local_write_and_ics_generation) ... ok

  Ran 20 tests in 0.048s — OK (All 20 tests passed)
  ```

---

## Session 3: Application Execution & Runner Fix

* **Timestamp**: 2026-10-21T10:11:00-04:00
* **User Prompt Received**: `run tp project 2.1`
* **Actions Taken**:
  1. Environment Preparation:
     * Verified `TP_Project_2.1` structure and dependencies.
     * Symlinked shared virtual environment `.venv` from `TP_Project_2`.
  2. Runner Bugfix:
     * Identified issue in `run.sh` where it attempted to invoke `uvicorn app.main:app`, failing because `app.main` is implemented as an `HTTPServer` rather than an ASGI app.
     * Updated `run.sh` to execute `python3 -m app.main` directly with `PYTHONPATH=.`.
  3. Verification:
     * Executed pytest test suite: all 20 tests passed.
     * Checked port 8081 availability.
     * Started background daemon process listening on `http://localhost:8081`.
     * Verified default personas: Alice Chen (@alice), Bob Martinez (@bob), Charlie Taylor (@charlie).

---

## Session 5: Reverting SMS Integration in Favor of Discord Account Integration

* **Timestamp**: 2026-10-25T14:40:00-04:00
* **User Prompt Received**:
  ```text
  instead of sms intergration for tp project 2.1 can you use a discord account? revert the sms impementation and use a discord instead
  ```
* **Actions Taken**:
  1. **Complete Reversion of SMS / MMS Integration**:
     * Removed `phone_number` from `UserProfile` model and serialized dictionaries in `app/models.py`.
     * Deleted obsolete `app/engine/sms_router.py` and deleted obsolete unit test suite `tests/test_sms.py`.
     * Removed `/api/sms/*` endpoints (`/api/sms/logs`, `/api/sms/system-number`, `/api/sms/webhook`, `/api/sms/simulate`) from `app/main.py`.
     * Removed smartphone simulator HTML markup, `.sms-*` and `.phone-*` CSS stylesheets, and SMS JavaScript handlers.
  2. **Discord Account Data Layer & Seed Metadata**:
     * Added `discord_username: str` and `discord_id: str` fields to `UserProfile` in `app/models.py`.
     * Updated seed personas in `app/engine/mock_data.py`:
       * Alice Chen: `alice#1337` (ID: `100000000000000001`)
       * Bob Martinez: `bob#2024` (ID: `100000000000000002`)
       * Charlie Taylor: `charlie#9090` (ID: `100000000000000003`)
     * Defined bot identity: `DISCORD_BOT_NAME = "CalMedia Bot"`, `DISCORD_BOT_ID = "999999999999999999"`, `DISCORD_DEFAULT_CHANNEL = "#calendar-sync"`.
  3. **Discord Command Router Engine (`app/engine/discord_router.py`)**:
     * Implemented `find_user_by_discord()` resolving users by Discord ID, username/tag (`alice#1337`), prefix handle, or `@mention` syntax.
     * Supported bot commands with `!` and `/` prefixes:
       * `!agenda [date]` / `/agenda`: Retrieves schedule and formats with Discord Blurple rich embed.
       * `!free [@friend/all] [date]`: Calculates mutual free windows using set intersection math with Prime time chips.
       * `!meet @friend HH:MM-HH:MM Title`: Pre-flight collision checker that detects conflicts or commits directly to attendees' `.ics` local stores.
       * `!privacy [BUSY/OPEN]`: Toggles schedule masking between transparent and "🔒 Busy".
       * `!help`: Comprehensive command syntax reference.
       * Image Attachments: Automatically verifies active calendar events and publishes photo moments to the campus feed.
     * Implemented Discord-standard rich embed payload generation (`title`, `description`, `color`, `fields`, `footer`, `image`).
  4. **Server API Endpoints (`app/main.py`)**:
     * Added `/api/discord/logs`: Returns in-memory Discord chat stream with author metadata, avatars, and embeds.
     * Added `/api/discord/bot-info`: Provides bot ID, active channel, and linked accounts reference.
     * Added `/api/discord/webhook` & `/api/discord/simulate`: Handles inbound interactions and logs messages.
  5. **Frontend Web GUI (`index.html`, `style.css`, `app.js`)**:
     * Implemented Tab 5: **Discord Bot Console** (`#calendar-sync`).
     * Added authentic Discord dark theme palette (`#313338`, `#2B2D31`, `#1E1F22`, `#5865F2`).
     * Designed Discord message stream with avatar bubbles, `BOT` badge pills, rich embed cards with color-coded side borders (Green, Yellow, Red, Blurple), quick command chips, and attachment pickers.
  6. **Automated Test Suite (`tests/test_discord.py`)**:
     * Created 10 comprehensive unit tests covering user lookup, `!agenda`, `!free`, `!meet` booking, `!meet` conflict detection, `!privacy` toggles, photo attachments, unregistered user handling, slash-command aliases, and embed structure.
     * Verified all 21 unit tests in `TP_Project_2.1` pass with 100% success rate.
  7. **Documentation Updates**:
     * Updated `start_instructions.md`, `Harness.md`, and `README.md` to reflect the new Discord integration architecture.




---

## Session 6: Account Creation, Campus Networking Between Two People, and GitHub Pages

* **Timestamp**: 2026-10-25T15:15:00-04:00
* **User Prompt Received**:
  ```text
  make account creation and networking between two people. As well as github pages
  ```
* **Actions Taken**:
  1. **Data Model Enhancements (`app/models.py`)**:
     * Added `incoming_requests: List[str]` and `outgoing_requests: List[str]` to the `UserProfile` dataclass.
     * Updated `to_dict()` serialization to persist request queues alongside friend lists.
  2. **Multi-User Ingestion & Networking Engine (`app/ingestion/sync_service.py`)**:
     * Implemented `create_user(data)`: Validates handle uniqueness, auto-formats `@handle`, configures avatar, bio, Discord tag, privacy mode, initializes calendar ingestion, and provisions local store directory.
     * Implemented `send_friend_request(from_uid, to_uid)`: Handles request queuing and reciprocal auto-connect (if target already sent a request, mutual friendship forms immediately).
     * Implemented `accept_friend_request(user_id, requester_id)`: Moves users into reciprocal mutual friends lists and cleans queues.
     * Implemented `decline_friend_request(user_id, requester_id)`: Removes pending invitations cleanly.
     * Implemented `unfriend(user_id, target_id)`: Removes reciprocal friendship.
     * Implemented `get_user_network(viewer_id)`: Returns full network relationships, mutual friends, pending incoming requests, and campus directory with event counts.
  3. **Backend API Endpoints (`app/main.py`)**:
     * Added `POST /api/users`: Account registration endpoint.
     * Added `GET /api/users/{id}/network`: User relationship graph.
     * Added `POST /api/users/{id}/connect`: Friend request dispatcher.
     * Added `POST /api/users/{id}/accept-friend`: Request acceptance.
     * Added `POST /api/users/{id}/decline-friend`: Request rejection.
     * Added `POST /api/users/{id}/unfriend`: Friendship removal.
  4. **Automated Unit Tests (`tests/test_social.py`)**:
     * Added `test_account_creation`: Verifies registration of new profile (Maya Lin `@maya`).
     * Added `test_networking_between_two_people`: Tests full lifecycle: friend request, incoming queue inspection, acceptance, and mutual friend verification.
     * Added `test_reciprocal_friend_request_auto_connect`: Verifies bidirectional request auto-resolution into mutual friendship.
     * Total test suite: **24 unit tests passing** (4 availability, 10 discord, 4 ingestion, 6 social/networking).
  5. **Interactive Web GUI (`app/templates/index.html`, `style.css`, `app.js`)**:
     * Added header button `✨ + Create Account` and registration modal (`#newAccountModal`) with emoji avatar picker, bio, Discord tag, calendar feed URL, and privacy settings.
     * Added Tab 3: **Campus Network & Friends** (`#networkTab`):
       * Unread incoming request badge (`#networkBadge`) with alert card.
       * Mutual friends grid with privacy indicators, 1-click availability comparison, 1-click hangout scheduling, Discord shortcut, and unfriend button.
       * Campus student directory with search filtering and 1-click connect buttons.
  6. **GitHub Pages Static Deployment (`site/`)**:
     * Built standalone static deployment directory `TP_Project_2.1/site/` with:
       * `site/index.html`: Complete CalMedia application dashboard.
       * `site/social.html`: Direct landing page supporting `#friends` deep-link matching `GC_Project_2.1/site/social.html#friends`.
       * `site/css/style.css`: Comprehensive dark-mode stylesheet.
       * `site/js/app.js`: Full client-side engine with persistent `localStorage` mock router, supporting offline and serverless GitHub Pages hosting with all 4 harness verification scenarios running client-side.
       * `site/images/`: Vector SVG illustrations for darkroom, soccer, and coffee moments.
     * Created `TP_Project_2.1/link.md` pointing to:
       `https://thomasperkins.github.io/calmedia/social.html#friends`
  7. **Documentation Updates**:
     * Updated `start_instructions.md`, `README.md`, `Harness.md`, and `link.md`.
