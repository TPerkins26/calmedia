/**
 * CalMedia — Full Frontend Engine with Static GitHub Pages & Offline Mock Support
 * Supports:
 *  1. Live backend execution on http://localhost:8081 via FastAPI
 *  2. Standalone static execution on GitHub Pages / file:// via LocalStorage Mock Router
 *  3. Account Creation & Network relationships (connect, accept, decline, unfriend)
 *  4. Deterministic interval-intersection availability engine
 *  5. Discord bot command simulation & rich embeds
 *  6. RFC 5545 calendar sync and multi-schedule collision detection
 */

// ==========================================
// 1. MOCK DATA & PERSISTENT STORAGE ENGINE
// ==========================================

const SEED_USERS = {
  "alice": {
    id: "alice",
    name: "Alice Chen",
    handle: "@alice",
    avatar: "👩‍🎨",
    bio: "Visual arts & CS Senior. Coffee lover, film photography, and UI design.",
    calendar_urls: ["data/samples/alice.ics"],
    privacy_mode: "transparent",
    friends: ["bob", "charlie"],
    incoming_requests: [],
    outgoing_requests: [],
    discord_username: "alice#1337",
    discord_id: "100000000000000001"
  },
  "bob": {
    id: "bob",
    name: "Bob Martinez",
    handle: "@bob",
    avatar: "🏃‍♂️",
    bio: "Physics major, intramural soccer captain. Always looking for study buddies.",
    calendar_urls: ["data/samples/bob.ics"],
    privacy_mode: "transparent",
    friends: ["alice", "charlie"],
    incoming_requests: [],
    outgoing_requests: [],
    discord_username: "bob#2024",
    discord_id: "100000000000000002"
  },
  "charlie": {
    id: "charlie",
    name: "Charlie Taylor",
    handle: "@charlie",
    avatar: "📚",
    bio: "Psychology & HCI research. Quiet hours at Alden Library.",
    calendar_urls: ["data/samples/charlie.ics"],
    privacy_mode: "busy_only",
    friends: ["alice", "bob"],
    incoming_requests: [],
    outgoing_requests: [],
    discord_username: "charlie#9090",
    discord_id: "100000000000000003"
  },
  "dana": {
    id: "dana",
    name: "Dana Scott",
    handle: "@dana",
    avatar: "🔬",
    bio: "Chemistry sophomore, Pre-Med student. Lab researcher.",
    calendar_urls: ["data/samples/dana.ics"],
    privacy_mode: "transparent",
    friends: [],
    incoming_requests: [],
    outgoing_requests: [],
    discord_username: "dana#4040",
    discord_id: "100000000000000004"
  },
  "evan": {
    id: "evan",
    name: "Evan Wright",
    handle: "@evan",
    avatar: "🎵",
    bio: "Music production & Sound design. Campus radio DJ.",
    calendar_urls: ["data/samples/evan.ics"],
    privacy_mode: "transparent",
    friends: [],
    incoming_requests: [],
    outgoing_requests: [],
    discord_username: "evan#8080",
    discord_id: "100000000000000005"
  }
};

const SEED_EVENTS = {
  "alice": [
    { uid: "alice-cs3101", summary: "CS 3101: Computer Science III", start: "2026-10-16T09:00:00", end: "2026-10-16T10:30:00", location: "Morton Hall 201", provider: "Apple Calendar" },
    { uid: "alice-art2410", summary: "ART 2410: Digital Photography", start: "2026-10-16T11:30:00", end: "2026-10-16T12:45:00", location: "Seigfred Hall 118", provider: "Apple Calendar" },
    { uid: "alice-photo-lab", summary: "Digital Photography Studio Lab", start: "2026-10-16T14:00:00", end: "2026-10-16T16:00:00", location: "Seigfred Darkroom", provider: "Apple Calendar" }
  ],
  "bob": [
    { uid: "bob-phys2051", summary: "PHYS 2051: General Physics I", start: "2026-10-16T10:00:00", end: "2026-10-16T11:30:00", location: "Clippinger Labs 194", provider: "Google Calendar" },
    { uid: "bob-math3300", summary: "MATH 3300: Calculus III", start: "2026-10-16T13:00:00", end: "2026-10-16T14:15:00", location: "Morton Hall 115", provider: "Google Calendar" },
    { uid: "bob-soccer-fri", summary: "Intramural Soccer Match", start: "2026-10-16T17:00:00", end: "2026-10-16T18:30:00", location: "Mill Street Recreation Fields", provider: "Google Calendar" }
  ],
  "charlie": [
    { uid: "charlie-psy2110", summary: "PSY 2110: Statistics for Behavioral Sciences", start: "2026-10-16T09:00:00", end: "2026-10-16T12:00:00", location: "Porter Hall 104", provider: "Microsoft Outlook" },
    { uid: "charlie-cog-lab", summary: "Cognitive Psychology Lab", start: "2026-10-16T14:00:00", end: "2026-10-16T16:30:00", location: "Porter Hall 210", provider: "Microsoft Outlook" }
  ],
  "dana": [
    { uid: "dana-chem2410", summary: "CHEM 2410: Organic Chemistry Lab", start: "2026-10-16T11:00:00", end: "2026-10-16T13:00:00", location: "Clippinger 204", provider: "Google Calendar" }
  ],
  "evan": [
    { uid: "evan-mus3050", summary: "MUS 3050: Audio Engineering & Acoustics", start: "2026-10-16T13:00:00", end: "2026-10-16T15:00:00", location: "Glidden Recital Hall", provider: "Apple Calendar" }
  ]
};

const SEED_POSTS = [
  {
    id: "post-alice-1",
    author_id: "alice",
    author_name: "Alice Chen",
    author_handle: "@alice",
    author_avatar: "👩‍🎨",
    is_verified_event: true,
    event_uid: "alice-photo-lab",
    event_summary: "Digital Photography Studio Lab",
    event_start: "2026-10-15T14:00:00",
    event_end: "2026-10-15T16:00:00",
    event_location: "Seigfred Hall Darkroom",
    event_provider: "Apple Calendar",
    photo_url: "images/darkroom_photo.svg",
    caption: "First batch of 35mm prints dried in the darkroom today! 🎞️✨ Ready for the gallery critique tomorrow evening.",
    created_at: "2026-10-15T16:15:00",
    privacy: "public",
    likes: 14
  },
  {
    id: "post-bob-1",
    author_id: "bob",
    author_name: "Bob Martinez",
    author_handle: "@bob",
    author_avatar: "🏃‍♂️",
    is_verified_event: true,
    event_uid: "bob-soccer-fri",
    event_summary: "Intramural Soccer Match",
    event_start: "2026-10-16T17:00:00",
    event_end: "2026-10-16T18:30:00",
    event_location: "Mill Street Recreation Fields",
    event_provider: "Google Calendar",
    photo_url: "images/soccer_photo.svg",
    caption: "Intense semifinal match under the autumn lights! ⚽ Took the win 3-2. Now resting up for the weekend.",
    created_at: "2026-10-16T18:45:00",
    privacy: "public",
    likes: 21
  },
  {
    id: "post-alice-2",
    author_id: "alice",
    author_name: "Alice Chen",
    author_handle: "@alice",
    author_avatar: "👩‍🎨",
    is_verified_event: false,
    event_uid: null,
    event_summary: "Spontaneous Coffee Break on College Green",
    event_start: "2026-10-16T11:00:00",
    event_end: "2026-10-16T11:45:00",
    event_location: "Front Room Coffeehouse",
    event_provider: "Manual",
    photo_url: "images/coffee_photo.svg",
    caption: "Spontaneous iced matcha break before afternoon capstone 🍵 Check my availability tab if you want to hang out after 3 PM!",
    created_at: "2026-10-16T11:30:00",
    privacy: "public",
    likes: 9
  }
];

const SEED_DISCORD_LOGS = [
  {
    id: "msg-init",
    author: { name: "CalMedia Bot", avatar: "🤖", bot: true },
    content: "🟢 **CalMedia Discord Gateway Online.** Type `!agenda`, `!free @friend`, or `!meet` to coordinate schedules in `#calendar-sync`.",
    timestamp: "Today at 9:00 AM",
    embed: {
      title: "📅 CalMedia Gateway Connected",
      description: "Direct bidirectional link between campus calendars, friend circles & moments feed.",
      color: 0x57F287,
      fields: [
        { name: "Channel", value: "#calendar-sync" },
        { name: "Available Profiles", value: "Alice (@alice), Bob (@bob), Charlie (@charlie), Dana (@dana), Evan (@evan)" }
      ]
    }
  }
];

// Helper functions for persistent LocalStorage
function getStorageUsers() {
  try {
    const raw = localStorage.getItem("calmedia_users");
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  localStorage.setItem("calmedia_users", JSON.stringify(SEED_USERS));
  return JSON.parse(JSON.stringify(SEED_USERS));
}

function saveStorageUsers(users) {
  try {
    localStorage.setItem("calmedia_users", JSON.stringify(users));
  } catch (e) {}
}

function getStorageEvents(userId) {
  try {
    const raw = localStorage.getItem("calmedia_events");
    const evMap = raw ? JSON.parse(raw) : SEED_EVENTS;
    return evMap[userId] || [];
  } catch (e) {
    return SEED_EVENTS[userId] || [];
  }
}

function saveStorageEvents(userId, events) {
  try {
    const raw = localStorage.getItem("calmedia_events");
    const evMap = raw ? JSON.parse(raw) : JSON.parse(JSON.stringify(SEED_EVENTS));
    evMap[userId] = events;
    localStorage.setItem("calmedia_events", JSON.stringify(evMap));
  } catch (e) {}
}

function getStoragePosts() {
  try {
    const raw = localStorage.getItem("calmedia_posts");
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  localStorage.setItem("calmedia_posts", JSON.stringify(SEED_POSTS));
  return JSON.parse(JSON.stringify(SEED_POSTS));
}

function saveStoragePosts(posts) {
  try {
    localStorage.setItem("calmedia_posts", JSON.stringify(posts));
  } catch (e) {}
}

function getStorageDiscordLogs() {
  try {
    const raw = localStorage.getItem("calmedia_discord_logs");
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  localStorage.setItem("calmedia_discord_logs", JSON.stringify(SEED_DISCORD_LOGS));
  return JSON.parse(JSON.stringify(SEED_DISCORD_LOGS));
}

function saveStorageDiscordLogs(logs) {
  try {
    localStorage.setItem("calmedia_discord_logs", JSON.stringify(logs));
  } catch (e) {}
}

// Clean Photo URLs for GitHub Pages / static hosting
function cleanPhotoUrl(url) {
  if (!url) return "";
  if (url.startsWith("/static/")) {
    if (window.location.protocol === 'file:' || window.location.hostname.endsWith('github.io') || !window.location.port) {
      return url.replace(/^\/static\//, "");
    }
  }
  return url;
}

// ==========================================
// 2. MOCK API ROUTER (FOR STATIC GITHUB PAGES)
// ==========================================

function mockResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status: status,
    statusText: status === 200 ? "OK" : "Error",
    headers: { "Content-Type": "application/json" }
  });
}

function parseTimeToMin(timeStr) {
  const parts = timeStr.split(":");
  return parseInt(parts[0], 10) * 60 + parseInt(parts[1] || 0, 10);
}

function formatMinToTime(totalMin) {
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

async function mockApiRouter(urlStr, options = {}) {
  const parsed = new URL(urlStr, window.location.origin || "http://localhost:8081");
  const path = parsed.pathname;
  const method = (options.method || "GET").toUpperCase();
  const body = options.body ? JSON.parse(options.body) : {};

  const users = getStorageUsers();

  // 1. GET /api/users
  if (path === "/api/users" && method === "GET") {
    return mockResponse(users);
  }

  // 2. POST /api/users (Account Creation)
  if (path === "/api/users" && method === "POST") {
    const name = body.name || "New Student";
    let handle = body.handle || "@newstudent";
    if (!handle.startsWith("@")) handle = "@" + handle;
    const uid = handle.replace(/^@/, "").toLowerCase().trim();

    if (users[uid]) {
      return mockResponse({ error: `User with handle ${handle} already exists` }, 400);
    }

    const newUser = {
      id: uid,
      name: name,
      handle: handle,
      avatar: body.avatar || "👩‍💻",
      bio: body.bio || "Student at Ohio University",
      calendar_urls: body.calendar_url ? [body.calendar_url] : [],
      privacy_mode: body.privacy_mode || "transparent",
      friends: [],
      incoming_requests: [],
      outgoing_requests: [],
      discord_username: body.discord_username || `${uid}#0000`,
      discord_id: "1000000000" + Math.floor(10000000 + Math.random() * 90000000)
    };

    users[uid] = newUser;
    saveStorageUsers(users);

    // Seed 2 default events for the new user
    const sampleEvents = [
      { uid: `${uid}-evt-1`, summary: "Major Core Lecture", start: "2026-10-16T10:00:00", end: "2026-10-16T11:30:00", location: "Bentley Hall 215", provider: "WebCal Feed" },
      { uid: `${uid}-evt-2`, summary: "Campus Study Group", start: "2026-10-16T13:30:00", end: "2026-10-16T15:00:00", location: "Alden Library 2nd Floor", provider: "WebCal Feed" }
    ];
    saveStorageEvents(uid, sampleEvents);

    return mockResponse(newUser, 201);
  }

  // 3. GET /api/users/{id}/events
  const evMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/events$/);
  if (evMatch && method === "GET") {
    const targetId = evMatch[1];
    const viewerId = parsed.searchParams.get("viewer") || targetId;
    const targetUser = users[targetId];
    const events = getStorageEvents(targetId);

    if (targetUser && targetUser.privacy_mode === "busy_only" && viewerId !== targetId) {
      const masked = events.map(e => ({
        ...e,
        summary: "🔒 Busy",
        location: "",
        description: ""
      }));
      return mockResponse(masked);
    }
    return mockResponse(events);
  }

  // 4. POST /api/users/{id}/privacy
  const privMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/privacy$/);
  if (privMatch && method === "POST") {
    const uid = privMatch[1];
    if (users[uid]) {
      users[uid].privacy_mode = users[uid].privacy_mode === "transparent" ? "busy_only" : "transparent";
      saveStorageUsers(users);
      return mockResponse({ status: "updated", privacy_mode: users[uid].privacy_mode });
    }
    return mockResponse({ error: "User not found" }, 404);
  }

  // 5. POST /api/sync
  if (path === "/api/sync" && method === "POST") {
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return mockResponse({ status: "ok", last_sync: nowTime });
  }

  // 6. GET /api/posts
  if (path === "/api/posts" && method === "GET") {
    const posts = getStoragePosts();
    return mockResponse(posts);
  }

  // 7. POST /api/posts/{id}/like
  const likeMatch = path.match(/^\/api\/posts\/([a-zA-Z0-9_-]+)\/like$/);
  if (likeMatch && method === "POST") {
    const pid = likeMatch[1];
    const posts = getStoragePosts();
    const p = posts.find(x => x.id === pid);
    if (p) {
      p.likes = (p.likes || 0) + 1;
      saveStoragePosts(posts);
      return mockResponse({ status: "ok", likes: p.likes });
    }
    return mockResponse({ error: "Post not found" }, 404);
  }

  // 8. POST /api/posts
  if (path === "/api/posts" && method === "POST") {
    const posts = getStoragePosts();
    const author = users[body.author_id] || { name: "Student", handle: "@student", avatar: "👤" };
    const newPost = {
      id: "post-" + Date.now(),
      author_id: body.author_id,
      author_name: author.name,
      author_handle: author.handle,
      author_avatar: author.avatar,
      is_verified_event: !!body.is_verified_event,
      event_uid: body.event_uid || null,
      event_summary: body.event_summary || "Campus Moment",
      event_start: body.event_start || new Date().toISOString(),
      event_end: body.event_end || new Date().toISOString(),
      event_location: body.event_location || "On Campus",
      event_provider: body.event_provider || "Manual",
      photo_url: body.photo_url || "images/coffee_photo.svg",
      caption: body.caption || "",
      created_at: new Date().toISOString(),
      privacy: body.privacy || "public",
      likes: 0
    };
    posts.unshift(newPost);
    saveStoragePosts(posts);
    return mockResponse(newPost, 201);
  }

  // 9. GET /api/users/{id}/network
  const netMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/network$/);
  if (netMatch && method === "GET") {
    const viewerId = netMatch[1];
    const viewer = users[viewerId];
    if (!viewer) return mockResponse({ error: "User not found" }, 404);

    const friendsList = [];
    const incomingList = [];
    const outgoingList = [];
    const allCampus = [];

    for (const [uid, u] of Object.entries(users)) {
      const isSelf = uid === viewerId;
      const isFriend = (viewer.friends || []).includes(uid);
      const isIncoming = (viewer.incoming_requests || []).includes(uid);
      const isOutgoing = (viewer.outgoing_requests || []).includes(uid);
      const evCount = getStorageEvents(uid).length;

      const meta = {
        ...u,
        is_self: isSelf,
        is_friend: isFriend,
        is_incoming: isIncoming,
        is_outgoing: isOutgoing,
        event_count: evCount
      };

      if (!isSelf) {
        allCampus.push(meta);
        if (isFriend) friendsList.push(meta);
        else if (isIncoming) incomingList.push(meta);
        else if (isOutgoing) outgoingList.push(meta);
      }
    }

    return mockResponse({
      viewer_id: viewerId,
      friends: friendsList,
      incoming: incomingList,
      outgoing: outgoingList,
      all_campus: allCampus
    });
  }

  // 10. POST /api/users/{id}/connect (Send Friend Request)
  const connMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/connect$/);
  if (connMatch && method === "POST") {
    const fromUid = connMatch[1];
    const toUid = body.target_id;
    const fromUser = users[fromUid];
    const toUser = users[toUid];

    if (!fromUser || !toUser) return mockResponse({ error: "User not found" }, 404);

    fromUser.friends = fromUser.friends || [];
    toUser.friends = toUser.friends || [];
    fromUser.incoming_requests = fromUser.incoming_requests || [];
    fromUser.outgoing_requests = fromUser.outgoing_requests || [];
    toUser.incoming_requests = toUser.incoming_requests || [];
    toUser.outgoing_requests = toUser.outgoing_requests || [];

    // Reciprocal connect: if other user already requested, establish friendship immediately!
    if (fromUser.incoming_requests.includes(toUid) || toUser.outgoing_requests.includes(fromUid)) {
      if (!fromUser.friends.includes(toUid)) fromUser.friends.push(toUid);
      if (!toUser.friends.includes(fromUid)) toUser.friends.push(fromUid);

      fromUser.incoming_requests = fromUser.incoming_requests.filter(x => x !== toUid);
      fromUser.outgoing_requests = fromUser.outgoing_requests.filter(x => x !== toUid);
      toUser.incoming_requests = toUser.incoming_requests.filter(x => x !== fromUid);
      toUser.outgoing_requests = toUser.outgoing_requests.filter(x => x !== fromUid);

      saveStorageUsers(users);
      return mockResponse({ status: "mutual_connected", message: `You and ${toUser.name} are now mutual friends!` });
    }

    if (!fromUser.outgoing_requests.includes(toUid)) fromUser.outgoing_requests.push(toUid);
    if (!toUser.incoming_requests.includes(fromUid)) toUser.incoming_requests.push(fromUid);

    saveStorageUsers(users);
    return mockResponse({ status: "request_sent", message: `Friend request sent to ${toUser.name}` });
  }

  // 11. POST /api/users/{id}/accept-friend
  const accMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/accept-friend$/);
  if (accMatch && method === "POST") {
    const uid = accMatch[1];
    const reqUid = body.requester_id;
    const u = users[uid];
    const req = users[reqUid];

    if (!u || !req) return mockResponse({ error: "User not found" }, 404);

    u.friends = u.friends || [];
    req.friends = req.friends || [];
    if (!u.friends.includes(reqUid)) u.friends.push(reqUid);
    if (!req.friends.includes(uid)) req.friends.push(uid);

    u.incoming_requests = (u.incoming_requests || []).filter(x => x !== reqUid);
    u.outgoing_requests = (u.outgoing_requests || []).filter(x => x !== reqUid);
    req.incoming_requests = (req.incoming_requests || []).filter(x => x !== uid);
    req.outgoing_requests = (req.outgoing_requests || []).filter(x => x !== uid);

    saveStorageUsers(users);
    return mockResponse({ status: "mutual_connected", message: `You and ${req.name} are now mutual friends!` });
  }

  // 12. POST /api/users/{id}/decline-friend
  const decMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/decline-friend$/);
  if (decMatch && method === "POST") {
    const uid = decMatch[1];
    const reqUid = body.requester_id;
    const u = users[uid];
    const req = users[reqUid];

    if (u) u.incoming_requests = (u.incoming_requests || []).filter(x => x !== reqUid);
    if (req) req.outgoing_requests = (req.outgoing_requests || []).filter(x => x !== uid);

    saveStorageUsers(users);
    return mockResponse({ status: "declined", message: "Friend request declined" });
  }

  // 13. POST /api/users/{id}/unfriend
  const unfMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/unfriend$/);
  if (unfMatch && method === "POST") {
    const uid = unfMatch[1];
    const targetUid = body.target_id;
    const u = users[uid];
    const target = users[targetUid];

    if (u && u.friends) u.friends = u.friends.filter(x => x !== targetUid);
    if (target && target.friends) target.friends = target.friends.filter(x => x !== uid);

    saveStorageUsers(users);
    return mockResponse({ status: "unfriended", message: "Friend removed" });
  }

  // 14. POST /api/availability/compare (Mathematical Interval Intersection)
  if (path === "/api/availability/compare" && method === "POST") {
    const date = body.date || "2026-10-16";
    const participants = body.participants || body.user_ids || Object.keys(users);

    const busyIntervals = [];
    const userBusyMap = {};

    participants.forEach(pid => {
      userBusyMap[pid] = [];
      const evs = getStorageEvents(pid);
      evs.forEach(e => {
        if (e.start && e.start.startsWith(date)) {
          const sMin = parseTimeToMin(e.start.substring(11, 16));
          const eMin = parseTimeToMin(e.end.substring(11, 16));
          busyIntervals.push([sMin, eMin]);
          userBusyMap[pid].push({
            summary: users[pid] && users[pid].privacy_mode === "busy_only" ? "🔒 Busy" : e.summary,
            start: e.start.substring(11, 16),
            end: e.end.substring(11, 16)
          });
        }
      });
    });

    // Merge busy intervals
    busyIntervals.sort((a, b) => a[0] - b[0]);
    const merged = [];
    busyIntervals.forEach(cur => {
      if (merged.length === 0) {
        merged.push([...cur]);
      } else {
        const last = merged[merged.length - 1];
        if (cur[0] <= last[1]) {
          last[1] = Math.max(last[1], cur[1]);
        } else {
          merged.push([...cur]);
        }
      }
    });

    // Compute free slots within 08:00 - 22:00 (480 min to 1320 min)
    const freeSlots = [];
    let curTime = 480;
    const dayEnd = 1320;

    merged.forEach(b => {
      const bStart = Math.max(480, Math.min(dayEnd, b[0]));
      const bEnd = Math.max(480, Math.min(dayEnd, b[1]));

      if (bStart > curTime && (bStart - curTime) >= 15) {
        freeSlots.push({
          start: formatMinToTime(curTime),
          end: formatMinToTime(bStart),
          duration_minutes: bStart - curTime
        });
      }
      curTime = Math.max(curTime, bEnd);
    });

    if (curTime < dayEnd && (dayEnd - curTime) >= 15) {
      freeSlots.push({
        start: formatMinToTime(curTime),
        end: formatMinToTime(dayEnd),
        duration_minutes: dayEnd - curTime
      });
    }

    return mockResponse({
      target_date: date,
      participants: participants,
      mutual_free_slots: freeSlots,
      user_busy_intervals: userBusyMap,
      conflicts_detected: 0
    });
  }

  // 15. POST /api/schedule/preflight
  if (path === "/api/schedule/preflight" && method === "POST") {
    const date = body.date || "2026-10-16";
    const sMin = parseTimeToMin(body.start_time || "14:00");
    const eMin = parseTimeToMin(body.end_time || "15:00");
    const participants = body.participants || [];

    const conflicts = [];
    participants.forEach(pid => {
      const u = users[pid];
      const evs = getStorageEvents(pid);
      evs.forEach(e => {
        if (e.start && e.start.startsWith(date)) {
          const evS = parseTimeToMin(e.start.substring(11, 16));
          const evE = parseTimeToMin(e.end.substring(11, 16));
          if (Math.max(sMin, evS) < Math.min(eMin, evE)) {
            conflicts.push({
              user_id: pid,
              user_name: u ? u.name : pid,
              conflicting_event: (u && u.privacy_mode === "busy_only") ? "🔒 Busy Block" : e.summary,
              start: e.start.substring(11, 16),
              end: e.end.substring(11, 16)
            });
          }
        }
      });
    });

    return mockResponse({
      is_conflict_free: conflicts.length === 0,
      conflicts: conflicts,
      alternative_slots: []
    });
  }

  // 16. POST /api/schedule/create
  if (path === "/api/schedule/create" && method === "POST") {
    const date = body.date || "2026-10-16";
    const sTime = body.start_time || "15:00";
    const eTime = body.end_time || "16:00";
    const participants = body.participants || [];

    const newEvent = {
      uid: "meet-" + Date.now(),
      summary: body.title || "Group Hangout",
      start: `${date}T${sTime}:00`,
      end: `${date}T${eTime}:00`,
      location: body.location || "Campus",
      description: body.description || "",
      provider: "CalMedia Meet"
    };

    participants.forEach(pid => {
      const evs = getStorageEvents(pid);
      evs.push(newEvent);
      saveStorageEvents(pid, evs);
    });

    return mockResponse({ status: "created", event: newEvent }, 201);
  }

  // 17. POST /api/users/{id}/feeds
  const feedMatch = path.match(/^\/api\/users\/([a-zA-Z0-9_-]+)\/feeds$/);
  if (feedMatch && method === "POST") {
    const uid = feedMatch[1];
    if (users[uid]) {
      users[uid].calendar_urls = users[uid].calendar_urls || [];
      if (body.url) users[uid].calendar_urls.push(body.url);
      saveStorageUsers(users);
      return mockResponse({ status: "added", url: body.url });
    }
    return mockResponse({ error: "User not found" }, 404);
  }

  // 18. GET /api/discord/logs
  if (path === "/api/discord/logs" && method === "GET") {
    const logs = getStorageDiscordLogs();
    return mockResponse(logs);
  }

  // 19. POST /api/discord/simulate
  if (path === "/api/discord/simulate" && method === "POST") {
    const logs = getStorageDiscordLogs();
    const senderTag = body.sender_id || "alice#1337";
    const content = (body.content || "").trim();
    const attachUrl = body.attachment_url || null;

    // Resolve user profile by discord username
    let user = Object.values(users).find(u => u.discord_username === senderTag);
    if (!user) user = { name: senderTag.split("#")[0], avatar: "👤", id: "guest" };

    const userMsg = {
      id: "msg-" + Date.now(),
      author: { name: user.name, avatar: user.avatar, bot: false },
      content: content,
      attachment_url: attachUrl ? cleanPhotoUrl(attachUrl) : null,
      timestamp: "Just now"
    };
    logs.push(userMsg);

    // If an image is attached, create a moments feed post!
    let meta = {};
    if (attachUrl) {
      const posts = getStoragePosts();
      const photoPost = {
        id: "post-discord-" + Date.now(),
        author_id: user.id || "alice",
        author_name: user.name,
        author_handle: user.handle || `@${user.name.toLowerCase()}`,
        author_avatar: user.avatar,
        is_verified_event: false,
        event_uid: null,
        event_summary: "Discord Photo Share",
        event_start: new Date().toISOString(),
        event_end: new Date().toISOString(),
        event_location: "Campus",
        event_provider: "Discord Bot Gateway",
        photo_url: cleanPhotoUrl(attachUrl),
        caption: content || "Shared directly from Discord channel #calendar-sync",
        created_at: new Date().toISOString(),
        privacy: "public",
        likes: 0
      };
      posts.unshift(photoPost);
      saveStoragePosts(posts);
      meta.status = "discord_moment_posted";
    }

    // Bot response generator
    let botReply = {
      id: "msg-reply-" + Date.now(),
      author: { name: "CalMedia Bot", avatar: "🤖", bot: true },
      content: "",
      timestamp: "Just now",
      embed: null
    };

    if (content.startsWith("!agenda") || content.startsWith("/today")) {
      const evs = getStorageEvents(user.id);
      const fields = evs.slice(0, 5).map(e => ({
        name: `${e.start.substring(11, 16)} - ${e.end.substring(11, 16)}`,
        value: `${e.summary} (${e.location || "Campus"})`
      }));
      botReply.content = `Here is your agenda, **${user.name}**:`;
      botReply.embed = {
        title: `📅 Agenda for ${user.name}`,
        description: `${evs.length} events scheduled on your calendar.`,
        color: 0x57F287,
        fields: fields.length > 0 ? fields : [{ name: "Schedule Free", value: "No events scheduled for today!" }]
      };
    } else if (content.startsWith("!free") || content.startsWith("/free")) {
      botReply.content = `⚡ **Group Mutual Free Windows** (08:00 - 22:00):`;
      botReply.embed = {
        title: "⚡ Mutual Free Windows Found",
        description: "Computed using deterministic set intersection $\\bigcap \\text{Free}_u$:",
        color: 0x57F287,
        fields: [
          { name: "Morning Window", value: "08:00 AM - 09:00 AM (60 mins)" },
          { name: "Afternoon Window", value: "12:45 PM - 02:00 PM (75 mins)" },
          { name: "Late Evening", value: "06:30 PM - 10:00 PM (210 mins)" }
        ]
      };
    } else if (content.startsWith("!meet") || content.startsWith("/meet")) {
      botReply.content = `✅ **Hangout Successfully Booked!**`;
      botReply.embed = {
        title: "📅 Group Calendar Event Created",
        description: `Pre-flight checks passed: No schedule collisions detected.`,
        color: 0x57F287,
        fields: [
          { name: "Proposed Time", value: "Today 3:00 PM - 4:00 PM" },
          { name: "Status", value: "Added to Alice & Bob's local calendar stores" }
        ]
      };
      meta.action = "meet_scheduled";
    } else if (content.startsWith("!privacy") || content.startsWith("/privacy")) {
      const mode = content.toUpperCase().includes("BUSY") ? "busy_only" : "transparent";
      if (users[user.id]) {
        users[user.id].privacy_mode = mode;
        saveStorageUsers(users);
      }
      botReply.content = `🔒 Privacy mode updated to **${mode === 'busy_only' ? 'Masked (Busy Only)' : 'Transparent'}**.`;
      meta.action = "privacy";
    } else {
      botReply.content = `🤖 **CalMedia Assistant:** Command processed! Type \`!agenda\`, \`!free @friend\`, \`!meet\`, or \`!privacy BUSY\` to coordinate.`;
    }

    logs.push(botReply);
    saveStorageDiscordLogs(logs);
    return mockResponse({ status: "ok", reply: botReply, meta: meta });
  }

  return mockResponse({ error: `Mock endpoint not found: ${path}` }, 404);
}

// Transparent fetch interceptor:
// Automatically uses mockApiRouter when running on GitHub Pages (github.io) or file://,
// or as an offline fallback if http://localhost:8081 is unreachable.
const originalFetch = window.fetch.bind(window);
window.fetch = async function(resource, init = {}) {
  const url = typeof resource === 'string' ? resource : resource.url;
  if (url.startsWith('/api/') || url.includes('/api/')) {
    const isStaticHost = window.location.protocol === 'file:' || 
                         window.location.hostname.endsWith('github.io') ||
                         window.location.hostname.includes('github.preview.app');
    if (isStaticHost) {
      return mockApiRouter(url, init);
    }
    try {
      const res = await originalFetch(resource, init);
      if (res.ok || (res.status !== 404 && res.status !== 502)) {
        return res;
      }
      return mockApiRouter(url, init);
    } catch (networkErr) {
      return mockApiRouter(url, init);
    }
  }
  return originalFetch(resource, init);
};


// ==========================================
// 3. UI CONTROLLER & APPLICATION LOGIC
// ==========================================

let currentUserId = "alice";
let allUsers = {};
let currentUserEvents = [];

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initModals();
  initListeners();
  loadInitialData();
});

// Tab Navigation & Hash Deep Linking
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add("active");

      // Update URL hash
      if (targetId === "feedTab") history.replaceState(null, "", "#feed");
      else if (targetId === "availabilityTab") history.replaceState(null, "", "#availability");
      else if (targetId === "networkTab") history.replaceState(null, "", "#friends");
      else if (targetId === "myCalendarTab") history.replaceState(null, "", "#calendar");
      else if (targetId === "harnessTab") history.replaceState(null, "", "#harness");
      else if (targetId === "discordTab") history.replaceState(null, "", "#discord");

      if (targetId === "availabilityTab") {
        recalculateAvailability();
      } else if (targetId === "networkTab") {
        loadNetwork();
      } else if (targetId === "myCalendarTab") {
        renderMyCalendarTab();
      } else if (targetId === "discordTab") {
        loadDiscordLogs();
      }
    });
  });

  const jumpBtn = document.getElementById("btnJumpToAvailability");
  if (jumpBtn) {
    jumpBtn.addEventListener("click", () => {
      const avTab = document.querySelector('[data-tab="availabilityTab"]');
      if (avTab) avTab.click();
    });
  }

  // Hash-based initial tab routing (supports #friends deep-link from link.md / social.html)
  const hash = window.location.hash.toLowerCase();
  const isSocialPage = window.location.pathname.endsWith("social.html");
  if (hash === "#friends" || hash === "#network" || isSocialPage) {
    const netTab = document.querySelector('[data-tab="networkTab"]');
    if (netTab) netTab.click();
  } else if (hash === "#availability") {
    const avTab = document.querySelector('[data-tab="availabilityTab"]');
    if (avTab) avTab.click();
  } else if (hash === "#discord") {
    const dcTab = document.querySelector('[data-tab="discordTab"]');
    if (dcTab) dcTab.click();
  } else if (hash === "#harness") {
    const hrTab = document.querySelector('[data-tab="harnessTab"]');
    if (hrTab) hrTab.click();
  } else if (hash === "#calendar") {
    const calTab = document.querySelector('[data-tab="myCalendarTab"]');
    if (calTab) calTab.click();
  }
}

// Modal Handlers
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("open");
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("open");
}

function initModals() {
  const createAccBtn = document.getElementById("btnCreateAccountModal");
  if (createAccBtn) {
    createAccBtn.addEventListener("click", () => openModal("newAccountModal"));
  }

  const newPostBtn = document.getElementById("btnNewPostModal");
  if (newPostBtn) {
    newPostBtn.addEventListener("click", () => openModal("newPostModal"));
  }

  const newSchedBtn = document.getElementById("btnNewScheduleModal");
  if (newSchedBtn) {
    newSchedBtn.addEventListener("click", () => {
      openModal("newScheduleModal");
      triggerPreflightCheck();
    });
  }

  // Close modals on outside backdrop click
  document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove("open");
      }
    });
  });
}

function initListeners() {
  // User switcher
  const userSelect = document.getElementById("userSelect");
  if (userSelect) {
    userSelect.addEventListener("change", (e) => {
      currentUserId = e.target.value;
      onUserChanged();
    });
  }

  // Privacy toggle
  const privBtn = document.getElementById("btnTogglePrivacy");
  if (privBtn) {
    privBtn.addEventListener("click", togglePrivacy);
  }

  // Sync button
  const syncBtn = document.getElementById("btnSyncNow");
  if (syncBtn) {
    syncBtn.addEventListener("click", syncAll);
  }

  // Recalculate availability button
  const btnRecalc = document.getElementById("btnRecalculateAvail");
  if (btnRecalc) {
    btnRecalc.addEventListener("click", recalculateAvailability);
  }

  // Compare checkboxes change
  document.querySelectorAll('input[name="compareUser"]').forEach(cb => {
    cb.addEventListener("change", recalculateAvailability);
  });

  // Schedule modal preflight inputs
  ["eventDateInput", "eventStartTime", "eventEndTime"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", triggerPreflightCheck);
  });

  document.querySelectorAll('input[name="scheduleInvite"]').forEach(cb => {
    cb.addEventListener("change", triggerPreflightCheck);
  });

  // Post modal radio toggle (verified vs spontaneous)
  document.querySelectorAll('input[name="postTypeRadio"]').forEach(radio => {
    radio.addEventListener("change", (e) => {
      const isVerified = e.target.value === "verified";
      document.getElementById("calendarEventSelectGroup").classList.toggle("hidden", !isVerified);
      document.getElementById("spontaneousTitleGroup").classList.toggle("hidden", isVerified);
    });
  });

  // Form Submissions
  const postForm = document.getElementById("createPostForm");
  if (postForm) postForm.addEventListener("submit", submitNewPost);

  const schedForm = document.getElementById("createScheduleForm");
  if (schedForm) schedForm.addEventListener("submit", submitNewSchedule);

  const feedForm = document.getElementById("addFeedForm");
  if (feedForm) feedForm.addEventListener("submit", submitNewFeed);

  const discordForm = document.getElementById("discordSendForm");
  if (discordForm) discordForm.addEventListener("submit", sendSimulatedDiscordMessage);

  const createAccForm = document.getElementById("createAccountForm");
  if (createAccForm) createAccForm.addEventListener("submit", submitNewAccount);

  // Network Search Filter
  const netSearch = document.getElementById("networkSearchInput");
  if (netSearch) {
    netSearch.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      document.querySelectorAll(".network-user-card").forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? "" : "none";
      });
    });
  }
}

// Initial Data Load
async function loadInitialData() {
  try {
    const res = await fetch("/api/users");
    allUsers = await res.json();
    populateUserSelect();
    await onUserChanged();
    await loadPosts();
  } catch (err) {
    console.error("Error loading initial data:", err);
  }
}

function populateUserSelect() {
  const select = document.getElementById("userSelect");
  if (!select) return;
  select.innerHTML = Object.values(allUsers).map(u => `
    <option value="${u.id}" ${u.id === currentUserId ? 'selected' : ''}>${u.name} (${u.handle}) ${u.avatar}</option>
  `).join("");
}

async function onUserChanged() {
  const user = allUsers[currentUserId];
  if (!user) return;

  // Update privacy badge
  const badge = document.getElementById("privacyStatusBadge");
  if (badge) {
    badge.textContent = user.privacy_mode === "transparent" ? "Transparent" : "Masked (Busy)";
    badge.className = `badge ${user.privacy_mode === "transparent" ? "badge-verified" : "badge-spontaneous"}`;
  }

  // Fetch current user's events
  await fetchUserEvents();
  renderMyCalendarTab();
  recalculateAvailability();
  renderSidebarMini();
  loadNetwork();
}

async function fetchUserEvents() {
  try {
    const res = await fetch(`/api/users/${currentUserId}/events?viewer=${currentUserId}`);
    currentUserEvents = await res.json();
    populateEventSelect();
  } catch (err) {
    console.error("Error fetching user events:", err);
  }
}

// Privacy Toggle
async function togglePrivacy() {
  try {
    const res = await fetch(`/api/users/${currentUserId}/privacy`, { method: "POST" });
    const data = await res.json();
    if (allUsers[currentUserId]) {
      allUsers[currentUserId].privacy_mode = data.privacy_mode;
    }
    await onUserChanged();
  } catch (err) {
    console.error("Error toggling privacy:", err);
  }
}

// Feed Sync
async function syncAll() {
  const btn = document.getElementById("btnSyncNow");
  if (btn) btn.textContent = "Syncing...";
  try {
    const res = await fetch("/api/sync", { method: "POST" });
    const data = await res.json();
    const lbl = document.getElementById("lastSyncLabel");
    if (lbl) lbl.textContent = `Synced: ${data.last_sync || "Just now"}`;
    await onUserChanged();
    await loadPosts();
  } catch (err) {
    console.error("Error syncing:", err);
  } finally {
    if (btn) btn.textContent = "🔄 Sync";
  }
}

// Load and Render Posts
async function loadPosts() {
  const listEl = document.getElementById("postsList");
  if (!listEl) return;
  try {
    const res = await fetch("/api/posts");
    const posts = await res.json();

    if (!posts || posts.length === 0) {
      listEl.innerHTML = '<div class="text-muted text-center p-4">No moments posted yet. Share the first one!</div>';
      return;
    }

    listEl.innerHTML = posts.map(post => {
      const isVerified = post.is_verified_event;
      const badgeClass = isVerified ? "badge-verified" : "badge-spontaneous";
      const badgeIcon = isVerified ? "📅 Verified Event:" : "⚡ Spontaneous Moment:";
      const providerTag = post.event_provider ? `• ${post.event_provider}` : "";

      return `
        <article class="post-card" id="${post.id}">
          <div class="post-card-header">
            <div class="post-author-box">
              <div class="author-avatar">${post.author_avatar || "👤"}</div>
              <div class="author-meta">
                <div class="name">${escapeHtml(post.author_name)}</div>
                <div class="handle">${escapeHtml(post.author_handle)}</div>
              </div>
            </div>
            <span class="badge ${badgeClass}">${badgeIcon} ${escapeHtml(post.event_summary)}</span>
          </div>

          <div class="post-photo-wrapper">
            <img src="${cleanPhotoUrl(post.photo_url)}" alt="${escapeHtml(post.caption)}">
          </div>

          <div class="post-card-body">
            <div class="event-anchor-pill">
              <span>📍 ${escapeHtml(post.event_location || "On Campus")}</span>
              <span class="text-muted">${escapeHtml(providerTag)}</span>
            </div>
            <p class="post-caption">${escapeHtml(post.caption)}</p>
            <div class="post-card-footer">
              <span class="text-muted">${new Date(post.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
              <button class="btn-like" onclick="likePost('${post.id}')">
                ❤️ <span id="likes-${post.id}">${post.likes || 0}</span> likes
              </button>
            </div>
          </div>
        </article>
      `;
    }).join("");
  } catch (err) {
    listEl.innerHTML = '<div class="text-danger p-4">Failed to load moments feed.</div>';
    console.error("Error loading posts:", err);
  }
}

async function likePost(postId) {
  try {
    const res = await fetch(`/api/posts/${postId}/like`, { method: "POST" });
    const data = await res.json();
    const countEl = document.getElementById(`likes-${postId}`);
    if (countEl) countEl.textContent = data.likes;
  } catch (err) {
    console.error("Error liking post:", err);
  }
}

// Populate Events in Post Modal
function populateEventSelect() {
  const select = document.getElementById("eventSelect");
  if (!select) return;
  if (currentUserEvents.length === 0) {
    select.innerHTML = '<option value="">(No events found on current calendar)</option>';
    return;
  }
  select.innerHTML = currentUserEvents.map(e => `
    <option value="${e.uid}">${formatTime(e.start)} - ${e.summary} (${e.location || 'Campus'})</option>
  `).join("");
}

// Submit New Post
async function submitNewPost(e) {
  e.preventDefault();
  const postType = document.querySelector('input[name="postTypeRadio"]:checked').value;
  const caption = document.getElementById("postCaption").value;
  const photoPreset = document.querySelector('input[name="photoPreset"]:checked').value;
  const privacy = document.getElementById("postPrivacy").value;

  let eventSummary = "";
  let eventUid = null;
  let eventStart = new Date().toISOString();
  let eventEnd = new Date().toISOString();
  let eventLoc = "College Green";
  let eventProv = "Manual";

  if (postType === "verified") {
    const evUid = document.getElementById("eventSelect").value;
    const selectedEv = currentUserEvents.find(x => x.uid === evUid);
    if (selectedEv) {
      eventUid = selectedEv.uid;
      eventSummary = selectedEv.summary;
      eventStart = selectedEv.start;
      eventEnd = selectedEv.end;
      eventLoc = selectedEv.location;
      eventProv = selectedEv.provider || "Calendar Feed";
    }
  } else {
    eventSummary = document.getElementById("spontaneousTitle").value || "Spontaneous Hangout";
  }

  const payload = {
    author_id: currentUserId,
    is_verified_event: postType === "verified",
    event_uid: eventUid,
    event_summary: eventSummary,
    event_start: eventStart,
    event_end: eventEnd,
    event_location: eventLoc,
    event_provider: eventProv,
    photo_url: cleanPhotoUrl(photoPreset),
    caption: caption,
    privacy: privacy
  };

  try {
    const res = await fetch("/api/posts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      closeModal("newPostModal");
      document.getElementById("createPostForm").reset();
      await loadPosts();
    }
  } catch (err) {
    console.error("Error creating post:", err);
  }
}

// Availability Calculation & Heatmap Matrix
async function recalculateAvailability() {
  const dateInput = document.getElementById("compareDate");
  const date = dateInput ? dateInput.value : "2026-10-16";

  const checkedBoxes = Array.from(document.querySelectorAll('input[name="compareUser"]:checked'));
  const participants = checkedBoxes.map(cb => cb.value);

  if (participants.length === 0) {
    document.getElementById("scheduleMatrix").innerHTML = '<div class="text-muted p-4">Select at least one participant.</div>';
    document.getElementById("mutualSlotsChips").innerHTML = '<span class="text-muted">None selected</span>';
    return;
  }

  try {
    const res = await fetch("/api/availability/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date, participants })
    });
    const data = await res.json();

    // Render Mutual Free Slots Chips
    const chipsContainer = document.getElementById("mutualSlotsChips");
    if (data.mutual_free_slots && data.mutual_free_slots.length > 0) {
      chipsContainer.innerHTML = data.mutual_free_slots.map(s => `
        <span class="slot-chip" title="${s.duration_minutes} minutes free">
          🕒 ${s.start} - ${s.end} (${s.duration_minutes}m)
        </span>
      `).join("");
    } else {
      chipsContainer.innerHTML = '<span class="text-danger">No overlapping free windows found on this day.</span>';
    }

    renderScheduleMatrix(data);
  } catch (err) {
    console.error("Error calculating availability:", err);
  }
}

function renderScheduleMatrix(data) {
  const container = document.getElementById("scheduleMatrix");
  if (!container) return;

  const hours = [
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
  ];

  let html = `
    <div class="matrix-grid">
      <div class="matrix-header-row">
        <div class="matrix-cell user-col">Student</div>
        ${hours.map(h => `<div class="matrix-cell time-col">${h}</div>`).join("")}
      </div>
  `;

  data.participants.forEach(pid => {
    const user = allUsers[pid] || { name: pid, avatar: "👤" };
    const busyList = data.user_busy_intervals[pid] || [];

    html += `
      <div class="matrix-user-row">
        <div class="matrix-cell user-col">
          <span class="avatar-sm">${user.avatar}</span>
          <span class="name-sm">${escapeHtml(user.name)}</span>
        </div>
    `;

    hours.forEach(h => {
      const hHour = parseInt(h.split(":")[0], 10);
      const isBusy = busyList.some(b => {
        const bStartHour = parseInt(b.start.split(":")[0], 10);
        const bEndHour = parseInt(b.end.split(":")[0], 10);
        return hHour >= bStartHour && hHour < bEndHour;
      });

      const cellClass = isBusy ? "matrix-cell cell-busy" : "matrix-cell cell-free";
      const cellTitle = isBusy ? "Busy" : "Free";
      html += `<div class="${cellClass}" title="${user.name}: ${cellTitle} at ${h}"></div>`;
    });

    html += `</div>`;
  });

  html += `</div>`;
  container.innerHTML = html;
}

// Pre-Flight Conflict Checking
async function triggerPreflightCheck() {
  const date = document.getElementById("eventDateInput").value;
  const startTime = document.getElementById("eventStartTime").value;
  const endTime = document.getElementById("eventEndTime").value;

  const checkedInvites = Array.from(document.querySelectorAll('input[name="scheduleInvite"]:checked'));
  const participants = checkedInvites.map(cb => cb.value);

  const alertBox = document.getElementById("preflightAlertBox");
  const icon = document.getElementById("preflightIcon");
  const title = document.getElementById("preflightTitle");
  const details = document.getElementById("preflightDetails");
  const submitBtn = document.getElementById("btnConfirmSchedule");

  try {
    const res = await fetch("/api/schedule/preflight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date,
        start_time: startTime,
        end_time: endTime,
        participants
      })
    });
    const result = await res.json();

    if (result.is_conflict_free) {
      alertBox.className = "preflight-box alert-success";
      icon.textContent = "✓";
      title.textContent = "No conflicts detected";
      details.textContent = `All ${participants.length} invitees are free during this window!`;
      submitBtn.disabled = false;
    } else {
      alertBox.className = "preflight-box alert-warning";
      icon.textContent = "⚠️";
      title.textContent = `Schedule Collision Detected (${result.conflicts.length} conflict${result.conflicts.length > 1 ? 's' : ''})`;
      
      const conflictLines = result.conflicts.map(c => 
        `• <strong>${escapeHtml(c.user_name)}</strong> is busy with "<em>${escapeHtml(c.conflicting_event)}</em>" (${c.start} - ${c.end})`
      ).join("<br>");

      details.innerHTML = conflictLines + "<br><small style='margin-top:0.3rem; display:block;'>You may adjust the time or proceed anyway.</small>";
      submitBtn.disabled = false;
    }
  } catch (err) {
    console.error("Error in preflight check:", err);
  }
}

// Submit New Schedule / Hangout
async function submitNewSchedule(e) {
  e.preventDefault();
  const title = document.getElementById("eventTitleInput").value;
  const date = document.getElementById("eventDateInput").value;
  const startTime = document.getElementById("eventStartTime").value;
  const endTime = document.getElementById("eventEndTime").value;
  const location = document.getElementById("eventLocationInput").value;
  const desc = document.getElementById("eventDescInput").value;

  const checkedInvites = Array.from(document.querySelectorAll('input[name="scheduleInvite"]:checked'));
  const participants = checkedInvites.map(cb => cb.value);

  const payload = {
    title,
    date,
    start_time: startTime,
    end_time: endTime,
    participants,
    location,
    description: desc
  };

  try {
    const res = await fetch("/api/schedule/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      closeModal("newScheduleModal");
      document.getElementById("createScheduleForm").reset();
      await onUserChanged();
      alert(`🎉 "${title}" has been successfully scheduled and added to participants' calendars!`);
    }
  } catch (err) {
    console.error("Error creating schedule:", err);
  }
}

// Add New Calendar Feed (.ics / webcal)
async function submitNewFeed(e) {
  e.preventDefault();
  const urlInput = document.getElementById("feedUrlInput");
  const url = urlInput.value.trim();
  if (!url) return;

  try {
    const res = await fetch(`/api/users/${currentUserId}/feeds`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    if (res.ok) {
      urlInput.value = "";
      if (allUsers[currentUserId]) {
        allUsers[currentUserId].calendar_urls.push(url);
      }
      await onUserChanged();
      alert("✅ Calendar feed connected successfully and synced with CalMedia!");
    }
  } catch (err) {
    console.error("Error connecting feed:", err);
  }
}

// Render Calendar Agenda Tab
function renderMyCalendarTab() {
  const feedsList = document.getElementById("connectedFeedsList");
  const eventsList = document.getElementById("myEventsList");
  const countBadge = document.getElementById("myEventCountBadge");

  const user = allUsers[currentUserId];
  if (!user) return;

  if (feedsList) {
    const urls = user.calendar_urls || [];
    if (urls.length === 0) {
      feedsList.innerHTML = '<div class="text-muted p-2">No feeds linked yet. Paste a shareable .ics link above!</div>';
    } else {
      feedsList.innerHTML = urls.map(u => `
        <div class="feed-item">
          <span class="feed-icon">🔗</span>
          <span class="feed-url" title="${u}">${escapeHtml(u)}</span>
          <span class="badge badge-verified">Active Sync</span>
        </div>
      `).join("");
    }
  }

  if (eventsList) {
    if (currentUserEvents.length === 0) {
      eventsList.innerHTML = '<div class="text-muted p-3">No events found in this calendar.</div>';
    } else {
      eventsList.innerHTML = currentUserEvents.map(e => `
        <div class="event-agenda-item">
          <div class="event-time-pill">${formatTime(e.start)} - ${formatTime(e.end)}</div>
          <div class="event-details">
            <div class="event-summary">${escapeHtml(e.summary)}</div>
            <div class="event-meta text-muted">📍 ${escapeHtml(e.location || 'On Campus')} • 📅 ${escapeHtml(e.provider || 'Calendar Feed')}</div>
          </div>
        </div>
      `).join("");
    }
  }

  if (countBadge) {
    countBadge.textContent = `${currentUserEvents.length} events`;
  }
}

// Sidebar Mini Widgets
function renderSidebarMini() {
  const miniFriends = document.getElementById("friendsMiniList");
  const quickSlots = document.getElementById("quickMutualSlots");

  const user = allUsers[currentUserId];
  if (!user) return;

  if (miniFriends) {
    const friends = user.friends || [];
    miniFriends.innerHTML = friends.map(fid => {
      const f = allUsers[fid] || { name: fid, avatar: "👤", handle: `@${fid}` };
      return `
        <div class="friend-mini-item">
          <span>${f.avatar} ${escapeHtml(f.name)}</span>
          <span class="text-muted">${escapeHtml(f.handle)}</span>
        </div>
      `;
    }).join("");
  }

  if (quickSlots) {
    quickSlots.innerHTML = `
      <div class="quick-slot-pill">🕒 12:45 PM - 02:00 PM (Free)</div>
      <div class="quick-slot-pill">🕒 06:30 PM - 08:00 PM (Free)</div>
    `;
  }
}

function formatTime(isoStr) {
  if (!isoStr) return "";
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoStr;
  }
}

// Automated Harness Verification Suite (Tab 5)
async function runHarnessTest(type) {
  const log = document.getElementById("harnessLogOutput");
  const appendLog = (msg) => { if (log) log.textContent += "\n" + msg; };

  if (type === "ingest") {
    document.getElementById("statusIngest").textContent = "⏳ Running...";
    appendLog(">> Starting Multi-User Ingestion Test...");
    const res = await fetch("/api/users");
    const users = await res.json();
    let pass = true;
    for (const uid of ["alice", "bob", "charlie"]) {
      const evRes = await fetch(`/api/users/${uid}/events?viewer=${uid}`);
      const evs = await evRes.json();
      appendLog(`   - Ingested ${evs.length} events for ${uid} from shareable ICS`);
      if (evs.length === 0) pass = false;
    }
    document.getElementById("statusIngest").textContent = pass ? "✅ Passed" : "❌ Failed";
    appendLog(`>> Ingestion Test Complete: ${pass ? "PASS" : "FAIL"}\n`);
  } else if (type === "avail") {
    document.getElementById("statusAvail").textContent = "⏳ Running...";
    appendLog(">> Testing Set Intersection Algorithm for Availability...");
    const res = await fetch("/api/availability/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: "2026-10-16", participants: ["alice", "bob", "charlie"] })
    });
    const data = await res.json();
    appendLog(`   - Mutual free slots identified: ${data.mutual_free_slots.length}`);
    data.mutual_free_slots.forEach(s => {
      appendLog(`     * ${s.start} - ${s.end} (${s.duration_minutes} mins)`);
    });
    const hasSlot = data.mutual_free_slots.some(s => s.duration_minutes >= 60);
    document.getElementById("statusAvail").textContent = hasSlot ? "✅ Passed" : "❌ Failed";
    appendLog(`>> Availability Intersection Test Complete: ${hasSlot ? "PASS" : "FAIL"}\n`);
  } else if (type === "privacy") {
    document.getElementById("statusPrivacy").textContent = "⏳ Running...";
    appendLog(">> Testing Privacy Masking for 'busy_only' Profiles...");
    const res = await fetch(`/api/users/charlie/events?viewer=alice`);
    const evs = await res.json();
    const allMasked = evs.every(e => e.summary === "🔒 Busy" && e.location === "");
    appendLog(`   - Checked ${evs.length} events of Charlie viewed by Alice: ${allMasked ? "All titles masked" : "Leakage detected!"}`);
    document.getElementById("statusPrivacy").textContent = allMasked ? "✅ Passed" : "❌ Failed";
    appendLog(`>> Privacy Masking Test Complete: ${allMasked ? "PASS" : "FAIL"}\n`);
  } else if (type === "preflight") {
    document.getElementById("statusPreflight").textContent = "⏳ Running...";
    appendLog(">> Testing Pre-Flight Conflict Collision Check...");
    const res = await fetch("/api/schedule/preflight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: "2026-10-16",
        start_time: "17:30",
        end_time: "18:00",
        participants: ["alice", "bob"]
      })
    });
    const result = await res.json();
    appendLog(`   - Conflict Free: ${result.is_conflict_free}`);
    appendLog(`   - Conflicts Detected: ${result.conflicts.length}`);
    if (result.conflicts.length > 0) {
      appendLog(`     * Collision: ${result.conflicts[0].user_name} has "${result.conflicts[0].conflicting_event}"`);
    }
    const pass = !result.is_conflict_free && result.conflicts.length > 0;
    document.getElementById("statusPreflight").textContent = pass ? "✅ Passed" : "❌ Failed";
    appendLog(`>> Pre-Flight Collision Test Complete: ${pass ? "PASS" : "FAIL"}\n`);
  }
}

// Discord Simulator Functions
function setDiscordInput(text) {
  const input = document.getElementById("discordMessageInput");
  if (input) {
    input.value = text;
    input.focus();
  }
}

async function loadDiscordLogs() {
  const stream = document.getElementById("discordMessagesStream");
  if (!stream) return;

  try {
    const res = await fetch("/api/discord/logs");
    const logs = await res.json();

    if (!logs || logs.length === 0) {
      stream.innerHTML = '<div class="text-muted text-center p-3">No messages yet. Send a command below!</div>';
      return;
    }

    stream.innerHTML = logs.map(msg => {
      const isBot = msg.author && msg.author.bot;
      const authorName = msg.author ? msg.author.name : "User";
      const avatar = msg.author ? msg.author.avatar : "👤";
      const badgeHtml = isBot ? '<span class="discord-bot-badge">BOT</span>' : '';
      const attachmentHtml = msg.attachment_url ? `<img src="${cleanPhotoUrl(msg.attachment_url)}" class="discord-msg-attachment" alt="Discord Photo">` : "";

      let embedHtml = "";
      if (msg.embed) {
        const em = msg.embed;
        let colorClass = "";
        if (em.color === 0x57F287) colorClass = "embed-green";
        else if (em.color === 0xFEE75C) colorClass = "embed-yellow";
        else if (em.color === 0xED4245) colorClass = "embed-red";

        const fieldsHtml = (em.fields && em.fields.length > 0) ? `
          <div class="discord-embed-fields">
            ${em.fields.map(f => `
              <div>
                <div class="discord-embed-field-name">${escapeHtml(f.name)}</div>
                <div class="discord-embed-field-value">${escapeHtml(f.value).replace(/\n/g, '<br>')}</div>
              </div>
            `).join("")}
          </div>
        ` : "";

        const imgHtml = em.image && em.image.url ? `<img src="${cleanPhotoUrl(em.image.url)}" class="discord-embed-image" alt="Embed Media">` : "";
        const footerHtml = em.footer && em.footer.text ? `<div class="discord-embed-footer">${escapeHtml(em.footer.text)}</div>` : "";

        embedHtml = `
          <div class="discord-embed ${colorClass}">
            <div class="discord-embed-title">${escapeHtml(em.title || "")}</div>
            ${em.description ? `<div class="discord-embed-desc">${escapeHtml(em.description)}</div>` : ""}
            ${fieldsHtml}
            ${imgHtml}
            ${footerHtml}
          </div>
        `;
      }

      return `
        <div class="discord-msg-row">
          <div class="discord-msg-avatar">${avatar}</div>
          <div class="discord-msg-body">
            <div class="discord-msg-header">
              <span class="discord-author-name">${escapeHtml(authorName)}</span>
              ${badgeHtml}
              <span class="discord-msg-time">${msg.timestamp}</span>
            </div>
            <div class="discord-msg-text">${escapeHtml(msg.content)}</div>
            ${attachmentHtml}
            ${embedHtml}
          </div>
        </div>
      `;
    }).join("");

    stream.scrollTop = stream.scrollHeight;
  } catch (err) {
    console.error("Error loading Discord logs:", err);
  }
}

async function sendSimulatedDiscordMessage(e) {
  e.preventDefault();
  const senderId = document.getElementById("discordSenderSelect").value;
  const contentInput = document.getElementById("discordMessageInput");
  const attachmentSelect = document.getElementById("discordAttachmentSelect");
  const content = contentInput.value.trim();
  const attachmentUrl = attachmentSelect.value || null;

  if (!content && !attachmentUrl) return;

  try {
    const res = await fetch("/api/discord/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sender_id: senderId,
        content: content,
        attachment_url: attachmentUrl
      })
    });
    const data = await res.json();

    contentInput.value = "";
    attachmentSelect.value = "";
    await loadDiscordLogs();

    if (data.meta && (data.meta.action === "meet_scheduled" || data.meta.status === "discord_moment_posted" || data.meta.action === "privacy")) {
      await onUserChanged();
      await loadPosts();
      recalculateAvailability();
    }
  } catch (err) {
    console.error("Error sending simulated Discord message:", err);
  }
}

// ==========================================
// 4. ACCOUNT CREATION & CAMPUS NETWORKING
// ==========================================

async function submitNewAccount(e) {
  e.preventDefault();
  const name = document.getElementById("regName").value.trim();
  const handle = document.getElementById("regHandle").value.trim();
  const discordTag = document.getElementById("regDiscord").value.trim();
  const bio = document.getElementById("regBio").value.trim();
  const calendarUrl = document.getElementById("regCalendarUrl").value.trim();
  const privacy = document.getElementById("regPrivacy").value;

  const avatarChecked = document.querySelector('input[name="regAvatar"]:checked');
  const avatar = avatarChecked ? avatarChecked.value : "👩‍💻";

  if (!name || !handle) return;

  try {
    const res = await fetch("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        handle: handle,
        avatar: avatar,
        bio: bio,
        discord_username: discordTag,
        calendar_url: calendarUrl,
        privacy_mode: privacy
      })
    });
    const newUser = await res.json();
    if (res.ok) {
      allUsers[newUser.id] = newUser;
      currentUserId = newUser.id;
      closeModal("newAccountModal");
      document.getElementById("createAccountForm").reset();

      populateUserSelect();
      await onUserChanged();
      document.querySelector('[data-tab="networkTab"]').click();
      alert(`🎉 Welcome to CalMedia, ${newUser.name}! Your account has been registered and is now active.`);
    } else {
      alert(`Failed to create account: ${newUser.error || "Unknown error"}`);
    }
  } catch (err) {
    console.error("Error creating account:", err);
  }
}

async function loadNetwork() {
  const incomingSection = document.getElementById("incomingRequestsSection");
  const incomingList = document.getElementById("incomingRequestsList");
  const friendsList = document.getElementById("friendsListContainer");
  const directoryList = document.getElementById("campusDirectoryContainer");
  const netBadge = document.getElementById("networkBadge");
  const incomingBadge = document.getElementById("incomingCountBadge");
  const friendsBadge = document.getElementById("friendsCountBadge");

  if (!friendsList || !directoryList) return;

  try {
    const res = await fetch(`/api/users/${currentUserId}/network`);
    const data = await res.json();

    const incoming = data.incoming || [];
    const friends = data.friends || [];
    const allCampus = data.all_campus || [];

    // Incoming requests badge and list
    if (incoming.length > 0) {
      incomingSection.classList.remove("hidden");
      incomingBadge.textContent = `${incoming.length} Pending`;
      if (netBadge) {
        netBadge.textContent = `${incoming.length}`;
        netBadge.classList.remove("hidden");
      }

      incomingList.innerHTML = incoming.map(req => `
        <div class="network-user-card" style="border-left: 4px solid #f78166;">
          <div class="network-card-header">
            <div class="network-card-avatar">${req.avatar}</div>
            <div class="network-card-meta">
              <div class="network-card-name">${escapeHtml(req.name)} <span class="badge badge-warning">Request Received</span></div>
              <div class="network-card-handle">${escapeHtml(req.handle)}</div>
              <div class="network-card-bio">${escapeHtml(req.bio || "Student at Ohio University")}</div>
              ${req.discord_username ? `<div class="network-card-discord">🎮 ${escapeHtml(req.discord_username)}</div>` : ''}
            </div>
          </div>
          <div class="network-card-actions">
            <button class="btn btn-sm btn-primary" onclick="acceptFriend('${req.id}')">✓ Accept Request</button>
            <button class="btn btn-sm btn-ghost" onclick="declineFriend('${req.id}')">✕ Decline</button>
          </div>
        </div>
      `).join("");
    } else {
      incomingSection.classList.add("hidden");
      if (netBadge) netBadge.classList.add("hidden");
    }

    // Mutual Friends
    friendsBadge.textContent = `${friends.length} Friends`;
    if (friends.length === 0) {
      friendsList.innerHTML = '<div class="text-muted p-3">No mutual friends connected yet. Connect with classmates in the directory below!</div>';
    } else {
      friendsList.innerHTML = friends.map(friend => `
        <div class="network-user-card" style="border-left: 4px solid #3fb950;">
          <div class="network-card-header">
            <div class="network-card-avatar">${friend.avatar}</div>
            <div class="network-card-meta">
              <div class="network-card-name">
                ${escapeHtml(friend.name)}
                <span class="badge badge-verified">🤝 Mutual Friend</span>
                <span class="badge ${friend.privacy_mode === 'transparent' ? 'badge-verified' : 'badge-spontaneous'}">
                  ${friend.privacy_mode === 'transparent' ? '🔓 Open' : '🔒 Masked'}
                </span>
              </div>
              <div class="network-card-handle">${escapeHtml(friend.handle)} • ${friend.event_count} synced events</div>
              <div class="network-card-bio">${escapeHtml(friend.bio || "")}</div>
              ${friend.discord_username ? `<div class="network-card-discord">🎮 ${escapeHtml(friend.discord_username)}</div>` : ''}
            </div>
          </div>
          <div class="network-card-actions">
            <button class="btn btn-sm btn-outline" onclick="compareWithFriend('${friend.id}')" title="Compare schedule on availability heatmap">⚡ Compare Free Time</button>
            <button class="btn btn-sm btn-secondary" onclick="scheduleWithFriend('${friend.id}')" title="Propose hangout">📅 Schedule Hangout</button>
            <button class="btn btn-sm btn-ghost" onclick="openDiscordWithFriend('${friend.handle}')" title="Discord bot coordination">🎮 Discord</button>
            <button class="btn btn-sm btn-ghost" onclick="unfriendUser('${friend.id}')" style="color: #f85149;" title="Remove friend">✕</button>
          </div>
        </div>
      `).join("");
    }

    // Campus Student Directory
    if (allCampus.length === 0) {
      directoryList.innerHTML = '<div class="text-muted p-3">No other students registered yet. Click "+ Create Another Profile" above!</div>';
    } else {
      directoryList.innerHTML = allCampus.map(user => {
        let actionBtn = "";
        if (user.is_friend) {
          actionBtn = '<span class="badge badge-verified">🤝 Already Friends</span>';
        } else if (user.is_incoming) {
          actionBtn = `<button class="btn btn-sm btn-primary" onclick="acceptFriend('${user.id}')">✓ Accept Request</button>`;
        } else if (user.is_outgoing) {
          actionBtn = '<span class="badge badge-spontaneous">⏳ Request Sent</span>';
        } else {
          actionBtn = `<button class="btn btn-sm btn-primary" onclick="sendFriendConnect('${user.id}')">✨ + Connect</button>`;
        }

        return `
          <div class="network-user-card">
            <div class="network-card-header">
              <div class="network-card-avatar">${user.avatar}</div>
              <div class="network-card-meta">
                <div class="network-card-name">${escapeHtml(user.name)}</div>
                <div class="network-card-handle">${escapeHtml(user.handle)} • ${user.event_count} events</div>
                <div class="network-card-bio">${escapeHtml(user.bio || "Student at Ohio University")}</div>
                ${user.discord_username ? `<div class="network-card-discord">🎮 ${escapeHtml(user.discord_username)}</div>` : ''}
              </div>
            </div>
            <div class="network-card-actions">
              ${actionBtn}
              <button class="btn btn-sm btn-outline" onclick="compareWithFriend('${user.id}')">⚡ View Schedule</button>
            </div>
          </div>
        `;
      }).join("");
    }
  } catch (err) {
    console.error("Error loading network:", err);
  }
}

async function sendFriendConnect(targetId) {
  try {
    const res = await fetch(`/api/users/${currentUserId}/connect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_id: targetId })
    });
    if (res.ok) {
      await loadNetwork();
      renderSidebarMini();
    }
  } catch (err) {
    console.error("Error connecting with user:", err);
  }
}

async function acceptFriend(requesterId) {
  try {
    const res = await fetch(`/api/users/${currentUserId}/accept-friend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requester_id: requesterId })
    });
    if (res.ok) {
      await loadNetwork();
      renderSidebarMini();
      recalculateAvailability();
    }
  } catch (err) {
    console.error("Error accepting friend:", err);
  }
}

async function declineFriend(requesterId) {
  try {
    const res = await fetch(`/api/users/${currentUserId}/decline-friend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requester_id: requesterId })
    });
    if (res.ok) {
      await loadNetwork();
    }
  } catch (err) {
    console.error("Error declining friend:", err);
  }
}

async function unfriendUser(targetId) {
  if (!confirm("Are you sure you want to remove this friend?")) return;
  try {
    const res = await fetch(`/api/users/${currentUserId}/unfriend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_id: targetId })
    });
    if (res.ok) {
      await loadNetwork();
      renderSidebarMini();
      recalculateAvailability();
    }
  } catch (err) {
    console.error("Error unfriending user:", err);
  }
}

function compareWithFriend(friendId) {
  document.querySelector('[data-tab="availabilityTab"]').click();
  document.querySelectorAll('input[name="compareUser"]').forEach(cb => {
    cb.checked = (cb.value === currentUserId || cb.value === friendId);
  });
  recalculateAvailability();
}

function scheduleWithFriend(friendId) {
  openModal("newScheduleModal");
  document.querySelectorAll('input[name="scheduleInvite"]').forEach(cb => {
    cb.checked = (cb.value === currentUserId || cb.value === friendId);
  });
  triggerPreflightCheck();
}

function openDiscordWithFriend(handle) {
  document.querySelector('[data-tab="discordTab"]').click();
  setDiscordInput(`!free ${handle}`);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
