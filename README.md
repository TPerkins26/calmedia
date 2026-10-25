# CalMedia — Calendar-Based Social Media Test Harness

The **Calendar-Based Social Media Test Harness** (`TP_Project_2.1`) is an interactive MVP, social scheduling engine, and verification environment. Extending the multi-provider calendar ingestion and deterministic scheduling engine of `TP_Project_2`, this platform introduces a **calendar-centric social network**.

It runs locally on `http://localhost:8081` with an interactive, responsive web GUI, real-time schedule intersection algorithms, pre-flight collision detection, and photo moments tied to verifiable calendar events.

---

## Features & Capabilities

### 1. Multi-User Calendar Link Ingestion & Sync

* **Shareable Feed Subscriptions**:
  * 🟢 **Google Calendar**: Secret or public iCal subscription link (`.ics`)
  * ⚪ **Apple Calendar**: iCloud public or webcal feed (`.ics` / `webcal://`)
  * 🔵 **Microsoft Outlook 365**: Published calendar feed (`.ics`)
  * 🔴 **Canvas LMS / Academic Portals**: Student/course calendar feed URL (`.ics`)
* **Multi-User Aggregation**: Manages independent calendar feeds for multiple friends simultaneously with background polling and offline caching in `data/cache/`.
* **Persona Seed Data**: Pre-configured with demo accounts (**Alice Chen**, **Bob Martinez**, and **Charlie Taylor**) in `data/samples/`.

### 2. Event Moments & Photo Journaling ("Proof of Event")

* **Flexible Hybrid Creation Model**:
  1. **Verified Calendar Event Post**: Users attach photos to real events parsed from their synced calendar feeds with a `📅 Verified Event: [Title]` badge.
  2. **Spontaneous Moment Post**: Allows users to post unscheduled memories with a `⚡ Spontaneous Moment` badge.
* **Photo Journaling Schema**: High-resolution image preview, caption, verified event anchor, location pill, author avatar/handle, and interactive likes.

### 3. Multi-Friend Availability Comparison Engine

All availability calculations are computed algorithmically using deterministic Python interval math without AI:

* **Recurrence Normalization**: Expands RFC 5545 `RRULE` recurrence rules and normalizes timestamps to local timezone (`America/New_York`).
* **Set Intersection Algorithm**:
  * Inverts busy intervals within daytime hours (8:00 AM – 10:00 PM) into user free spans.
  * Computes mathematical set intersection across all selected participants:
    $$\text{Free}_{\text{Group}} = \bigcap_{u \in \text{Participants}} \text{Free}_u$$
* **Social Hour Highlighting**: Identifies prime social slots (Lunch 11:30–13:30 and Evenings 17:00–21:00) with 1-click **"Schedule Together"** action.
* **User Privacy Toggle**: Users can toggle between **Full Transparency** (friends see event names and locations) and **Masked (Busy)** (blocks out time intervals as `🔒 Busy` without disclosing personal details).

### 4. Collaborative Social Scheduling & Conflict Detection

* **Real-Time Pre-Flight Group Conflict Check**:
  * Dynamically evaluates proposed start/end times against all invitees' active calendars before confirming.
  * Alerts on collisions (e.g., *"Warning: Bob is busy with Intramural Soccer (17:00–18:30)"*) and suggests unconflicted alternatives.
* **Local Mock ICS Store & Invite Generation**:
  * Commits confirmed events to each attendee's local mock store (`data/local_store/<user_id>.ics`).
  * Generates standard RFC 5545 `.ics` downloadable calendar invitation file with `VEVENT` and `ATTENDEE` tags.

### 5. Interactive Web GUI (`http://localhost:8081`)

* **Header Bar**: Live port 8081 indicator, persona switcher dropdown, one-click privacy toggle, last sync indicator, and quick-action buttons.
* **Moments Feed Tab**: Social cards showing photos, captions, and verified event badges.
* **Availability Heatmap Tab**: Multi-friend checkboxes, date picker, highlighted mutual free blocks, and side-by-side participant schedule matrix.
* **My Calendar & Feeds Tab**: Ingestion manager to connect new shareable calendar URLs and view active daily agenda.
* **Test Harness Tab**: Interactive test runner executing client-side verification steps directly in the browser.

---

## Tech Stack

* **Language**: Python 3.10+ (tested on Python 3.14)
* **Backend**: FastAPI / Uvicorn (with standard library zero-dependency fallback server)
* **Calendar Parsing & Serialization**: RFC 5545 `.ics` parser with `RRULE` recurrence expansion
* **Frontend**: Modern HTML5, CSS3, Vanilla JavaScript (ES modules)
* **Testing**: Python `unittest` / `pytest`

---

## Quick Start

### 1. Launch the Application

Run the startup script:

```bash
cd TP_Project_2.1
./run.sh
```

Or start directly with Python:

```bash
python3 -m app.main
```

Open your browser and navigate to:

```
http://localhost:8081
```

### 2. Run the Automated Test Suite

Run the full suite of unit and integration tests:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

---

## REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/users` | `GET` | Lists all users with profile metadata and privacy settings |
| `POST /api/users` | `POST` | Registers a new student profile (name, handle, avatar, bio, discord, calendar URL) |
| `GET /api/users/{id}` | `GET` | Fetches details for a specific user |
| `POST /api/users/{id}/privacy` | `POST` | Toggles privacy mode between `transparent` and `busy_only` |
| `GET /api/users/{id}/events` | `GET` | Retrieves user's events (with privacy masking if viewed by another user) |
| `GET /api/users/{id}/network` | `GET` | Retrieves full friend graph, pending requests, and campus directory |
| `POST /api/users/{id}/connect` | `POST` | Sends a friend connection request (auto-connects if reciprocal request exists) |
| `POST /api/users/{id}/accept-friend` | `POST` | Accepts an incoming friend request, establishing mutual friendship |
| `POST /api/users/{id}/decline-friend` | `POST` | Declines an incoming friend request |
| `POST /api/users/{id}/unfriend` | `POST` | Removes mutual friendship between two users |
| `POST /api/users/{id}/feeds` | `POST` | Adds a new shareable `.ics` or `webcal://` calendar link |
| `POST /api/sync` | `POST` | Refreshes and re-caches all connected calendar feeds |
| `GET /api/posts` | `GET` | Retrieves chronological feed of event photo moments |
| `POST /api/posts` | `POST` | Creates a verified calendar event post or spontaneous moment |
| `POST /api/posts/{id}/like` | `POST` | Increments like count on a moment post |
| `POST /api/availability/compare`| `POST` | Calculates mutual free time intersection across selected participants |
| `POST /api/schedule/preflight` | `POST` | Evaluates proposed times for conflicts across all invitees' calendars |
| `POST /api/schedule/create` | `POST` | Commits event to local stores and outputs RFC 5545 `.ics` payload |
| `POST /api/discord/webhook` | `POST` | Inbound Discord interaction webhook & bot gateway |
| `POST /api/discord/simulate`| `POST` | Interactive browser-based Discord bot console simulator endpoint |
| `GET /api/discord/logs` | `GET` | Fetches recent Discord channel chat logs and embeds |
| `GET /api/discord/bot-info` | `GET` | Returns Discord bot metadata and linked demo accounts |
| `GET /api/health` | `GET` | Health check endpoint returning port and status |

---

## GitHub Pages Deployment

CalMedia features full **GitHub Pages static deployment** in `site/`:
* **Live GitHub Pages URL**: 👉 **[https://thomasperkins.github.io/calmedia/social.html#friends](https://thomasperkins.github.io/calmedia/social.html#friends)**
* **Standalone Execution**: Runs 100% in the browser using an embedded `localStorage` mock engine, interval-math availability intersection, pre-flight conflict collision detection, and Discord console simulation.
* **Direct Landing Link**: Documented in [`link.md`](file:///home/thoma/htc/TP_Project_2.1/link.md).

---

## Project Structure

```text
TP_Project_2.1/
├── link.md                    # Live GitHub Pages link (https://thomasperkins.github.io/calmedia/social.html#friends)
├── AiLogs.md                  # Comprehensive AI prompt and audit trail
├── Harness.md                 # Test Harness Specification document
├── README.md                  # Documentation and API reference
├── start_instructions.md      # Step-by-step startup and testing guide
├── requirements.txt           # Python dependencies
├── run.sh                     # Application launch script
├── .env                       # Active environment variables
├── .env.example               # Template environment configuration
├── site/                      # Complete GitHub Pages static application
│   ├── index.html             # Static CalMedia dashboard
│   ├── social.html            # Campus Network & Friends landing page (#friends)
│   ├── css/style.css          # Standalone styles
│   ├── js/app.js              # Standalone client engine with localStorage persistence
│   └── images/                # Vector SVG illustrations
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration and path settings
│   ├── models.py              # Data structures (users, posts, events, availability)
│   ├── main.py                # Web server, API routes, and static handler
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── parser.py          # RFC 5545 .ics parser & recurrence expander
│   │   ├── availability.py    # Group schedule intersection & pre-flight checker
│   │   ├── mock_data.py       # Seed personas and demo moments
│   │   └── discord_router.py   # Discord bot command parser, photo attachments & embeds
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── sync_service.py    # Multi-user calendar feed ingestion & caching
│   ├── writers/
│   │   ├── __init__.py
│   │   └── local_writer.py    # Local mock store (.ics) writer & invite exporter
│   ├── templates/
│   │   └── index.html         # CalMedia dashboard GUI
│   └── static/
│       ├── css/
│       │   └── style.css      # Dark-mode styling, Discord channel frame, and UI layout
│       ├── js/
│       │   └── app.js         # Reactive client logic and API integration
│       └── images/            # Vector illustrations for event moments
│           ├── darkroom_photo.svg
│           ├── soccer_photo.svg
│           └── coffee_photo.svg
├── data/
│   ├── samples/               # Seed RFC 5545 calendar files (Alice, Bob, Charlie)
│   ├── cache/                 # Local cache of remote feeds
│   ├── local_store/           # Local write stores for scheduled events
│   └── uploads/               # Photo upload directory
└── tests/
    ├── test_ingestion.py      # Calendar parsing and feed sync tests
    ├── test_availability.py   # Overlap math and conflict validation tests
    ├── test_social.py         # Posts, likes, and local store writer tests
    └── test_discord.py        # Discord bot commands, preflight checks, and embed tests
```
