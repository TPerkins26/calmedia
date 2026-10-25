# Start Instructions — CalMedia (`TP_Project_2.1`)

This guide explains how to set up, configure, start, and stop the **Calendar-Based Social Media Test Harness** (`TP_Project_2.1`).

---

## If this is confusing you can also try asking your agent to run it for you

---

---

## 1. Quick Start (1 Command)

If your environment is already set up, simply execute the runner script from inside the `TP_Project_2.1` directory:

```bash
cd /home/thoma/htc/TP_Project_2.1
./run.sh
```

Once started, open your web browser to:
👉 **[http://localhost:8081](http://localhost:8081)**

---

## 2. First-Time Setup & Prerequisites

### Prerequisites
* **Python**: 3.10+ (tested on Python 3.14).
* **Virtual Environment**: A Python `.venv` with the packages in `requirements.txt`.

### Setup Option A: Use Existing Virtual Environment (Recommended)
You can link the existing `.venv` from `TP_Project_2`:

```bash
cd /home/thoma/htc/TP_Project_2.1
ln -s ../TP_Project_2/.venv .venv
```

### Setup Option B: Create a Fresh Virtual Environment
```bash
cd /home/thoma/htc/TP_Project_2.1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Configuration (`.env`)

Configuration settings are stored in [`.env`](file:///home/thoma/htc/TP_Project_2.1/.env):

```env
PORT=8081
HOST=0.0.0.0
SYNC_INTERVAL_MINUTES=15
TIMEZONE=America/New_York
MOCK_WRITE_MODE=true
UPLOAD_DIR=data/uploads
CACHE_DIR=data/cache
LOCAL_STORE_DIR=data/local_store
```

* **`PORT`**: Web server port (default is `8081`).
* **`HOST`**: Network host binding (`0.0.0.0` listens on all local interfaces).
* **`TIMEZONE`**: IANA timezone for event normalization (default: `America/New_York`).
* **`MOCK_WRITE_MODE`**: When `true`, created events are committed to local `.ics` stores rather than external APIs.

---

## 4. Starting the Server

### Method 1: Using the Shell Runner (`run.sh`)
```bash
cd /home/thoma/htc/TP_Project_2.1
./run.sh
```
*Note: Make sure `run.sh` has executable permissions: `chmod +x run.sh`.*

### Method 2: Running Directly with Python
Because `app.main` is implemented using Python's standard library `HTTPServer`, run it as a module:

```bash
cd /home/thoma/htc/TP_Project_2.1
export PYTHONPATH=.
.venv/bin/python3 -m app.main
```

You should see:
```text
================================================================
 Calendar Social Media Test Harness listening on http://localhost:8081
 Default Personas: Alice Chen (@alice), Bob Martinez (@bob), Charlie Taylor (@charlie)
================================================================
```

---

## 5. How to Stop the Server

### If Running in the Foreground
Press **`CTRL + C`** in the terminal where the server is running.

### If Running in the Background
To release port `8081` and terminate any running instance:

```bash
fuser -k 8081/tcp
```
Or find and terminate the Python process:
```bash
pkill -f "app.main"
```

---

## 6. Running the Automated Test Suite

To run the full suite of unit and integration tests:

```bash
cd /home/thoma/htc/TP_Project_2.1
PYTHONPATH=. .venv/bin/pytest
```

This verifies:
1. **Calendar Ingestion**: Multi-user `.ics` parsing and normalization.
2. **Availability Engine**: Group free-time set intersections and prime social slot detection.
3. **Pre-Flight Conflict Checks**: Multi-calendar collision detection.
4. **Social & Moments**: Photo journaling posts, verified event badges, and likes.
5. **Discord Bot Integration**: Inbound bot command routing (`!free`, `!meet`, `!agenda`, `!privacy`), photo moment attachments, and rich embeds.

---

---

## 7. Using the Web GUI (`http://localhost:8081` & GitHub Pages)

When you visit **`http://localhost:8081`** (or open the GitHub Pages link):

1. **Persona Switcher & Account Creation (Header)**:
   * Toggle between **Alice Chen** (`@alice`), **Bob Martinez** (`@bob`), **Charlie Taylor** (`@charlie`), and any newly created profiles.
   * Click **`✨ + Create Account`** to register a new student profile with custom name, `@handle`, emoji avatar, bio, Discord tag, privacy mode, and optional calendar feed link.
2. **Moments Feed Tab**:
   * Browse photo posts with `📅 Verified Event: [Title]` badges.
   * Post new photo moments (either attached to real calendar events or spontaneous).
3. **Availability Heatmap Tab**:
   * Select friends with checkboxes to instantly compute mutual free time slots via interval intersection.
   * Click **"Schedule Together"** to propose a hangout with live pre-flight conflict validation.
4. **Campus Network & Friends Tab (`#friends`)**:
   * **Incoming Requests**: Receive alerts when classmates send friend requests; accept or decline with 1-click.
   * **Mutual Friends**: View connected friends, their privacy mode, and synced events. Compare schedules, schedule hangouts, open Discord coordination, or unfriend.
   * **Campus Directory**: Discover registered students across campus and send connection requests.
5. **My Calendar & Feeds Tab**:
   * View the active user's daily agenda.
   * Add external calendar subscription URLs (Google, Apple, Outlook, Canvas).
6. **Discord Bot Console Tab**:
   * Test conversational Discord bot interactions directly in the browser via `#calendar-sync`.
   * Try commands like: `!free @bob`, `!agenda`, `!meet @bob 15:00-16:00 Coffee`, or `!privacy BUSY`.
   * Attach photos to automatically broadcast event-anchored moments to the feed!
7. **Test Harness & Verification Tab**:
   * Run automated in-browser verification scenarios for Multi-User Ingestion, Availability Intersection, Privacy Masking, and Pre-Flight Collision detection with full console logs.

---

## 8. GitHub Pages Deployment (`site/`)

CalMedia features full **GitHub Pages static deployment** located in the `site/` folder:

* **Live GitHub Pages URL**: 👉 **[https://thomasperkins.github.io/calmedia/social.html#friends](https://thomasperkins.github.io/calmedia/social.html#friends)**
* **Local Static Viewing**: You can open [`site/index.html`](file:///home/thoma/htc/TP_Project_2.1/site/index.html) or [`site/social.html`](file:///home/thoma/htc/TP_Project_2.1/site/social.html) directly in any browser without running a backend server.
* **Client-Side Engine**:
  * Implements a complete in-browser mock router backed by `localStorage`.
  * Pre-populated with 5 student profiles (Alice, Bob, Charlie, Dana, Evan) and realistic course schedules.
  * Deterministic interval-math availability intersection, pre-flight conflict checking, Discord command simulation, and full friend request lifecycle execute 100% in JavaScript.

---

## 9. Troubleshooting

* **`Port 8081 is already in use`**:
  Run `fuser -k 8081/tcp` to terminate any previous process still holding the port.
* **`Attribute 'app' not found in module 'app.main'`**:
  Do not use `uvicorn app.main:app`. The application uses Python's built-in `HTTPServer` and must be launched with `python3 -m app.main` or `./run.sh`.
* **Missing packages**:
  Activate your virtual environment and run `pip install -r requirements.txt`.


