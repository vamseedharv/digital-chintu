# Roadmap

Strategic sequencing, organized around the existing
[docs/features/](docs/features) numbering (001–050) — that numbering already
encodes the intended build order from the original Foundation pack; this
groups it into phases and states what's actually done vs. open today. Not a
committed schedule with dates — see [BACKLOG.md](BACKLOG.md) for granular,
short-horizon items instead.

## Phase 0 — Foundation — ✅ Done, frozen at `v0.2.0`

`001_Project_Setup` through `009_Assistant_Onboarding`. Status reconciled
per-doc (see each file's own Status note). Frozen after two review passes
(UI-specific, then full architecture) with every approved, non-feature
finding fixed — see [CHANGELOG.md](CHANGELOG.md)'s `[0.2.0]` entry and
[REPO_HEALTH_REPORT.md](REPO_HEALTH_REPORT.md):

| Feature | Status |
|---|---|
| 001 Project Setup | ✅ Done |
| 002 Docker | ✅ Done (delivered under 001) |
| 003 CI/CD | ✅ Done (delivered under 001; CD itself still open) |
| 004 Backend Core | ⚠️ Mostly done (error-response format, request middleware still open) |
| 005 Frontend Framework | ✅ Done (application shell, routing, component library) |
| 006 Theme Engine | ✅ Core done (custom spacing scale and broader component library deferred to real UI features that need them) |
| 007 Dashboard | ✅ Done (added after the freeze — widget-hosting home screen, see docs/features/007_Dashboard.md) |
| 008 Settings | ❌ Not started (env-var config only, no UI/API) |
| 009 Assistant Onboarding | ❌ Not started (name is configurable, but no onboarding flow) |

## Phase 1 — Plugin Framework — ✅ Done

`010_Plugin_Framework`. The extension point (discovery mechanism, plugin
interface, dynamic router registration) is built — see
[docs/features/010_Plugin_Framework.md](docs/features/010_Plugin_Framework.md)
and [docs/architecture/05_PLUGIN_SDK.md](docs/architecture/05_PLUGIN_SDK.md).
No real plugin exists yet; that's Phase 8 (`041_Home_Assistant`,
`042_Device_Control`).

## Phase 2 — Voice Pipeline

`011_Wake_Word`, `012_Speech_To_Text`, `013_Text_To_Speech`,
`014_Conversation_UI`, `031_Voice_Settings`, `032_Multilingual`. Depends on
OpenWakeWord / Whisper.cpp / Piper (per
[docs/Foundation/04_Tech_Stack.md](docs/Foundation/04_Tech_Stack.md)) — none
of these are integrated yet. Raspberry Pi resource constraints (CPU/RAM for
on-device STT/TTS) should be validated early in this phase, not assumed.

## Phase 3 — AI & Context

`015_Intent_Router`, `016_Session_Memory`, `033_Context_Memory`,
`034_Search`. Depends on Phase 2 for voice-driven input, but intent routing
over text input alone could start independently.

## Phase 4 — Productivity

`017_Reminders`, `018_Alarms`, `019_Todo`, `020_Shopping_List`, `021_Notes`,
`022_Google_Calendar`. **Reminders/Alarms are the first features that need
the scheduler** (`backend/app/core/scheduler.py`, wired but idle) and the
first database models (nothing exists in `backend/app/db/` beyond
engine/session scaffolding — introduce Alembic at that point, not before).

## Phase 5 — Media & Info

`023_Weather`, `024_News`, `025_Spotify`, `026_YouTube`, `027_Photo_Frame`,
`028_Media_Controller`. Each is a third-party integration — API keys/OAuth
handling will need a secrets story beyond today's plain `.env` (see
[docs/architecture/06_SECURITY.md](docs/architecture/06_SECURITY.md)).

## Phase 6 — UI Depth

`029_Notifications`, `030_Dynamic_UI`, `035_File_Manager`,
`048_Admin_Panel`. This is where the UI Design System
([docs/architecture/09_UI_DESIGN_SYSTEM.md](docs/architecture/09_UI_DESIGN_SYSTEM.md))
needs its typography/spacing/token system — extract shared primitives here,
once there's more than the two existing components to justify it.

## Phase 7 — Clients

`038_Mobile_API`, `039_Android_App`, `040_Web_App`. `frontend-mobile/`'s
framework (native vs. React Native) still needs to be decided — see its own
`README.md`. This is also the natural point to revisit the backend's
`snake_case` JSON vs. a generated/transformed TypeScript client (see
[DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md)) now that a second client exists.

## Phase 8 — Plugin Ecosystem

`041_Home_Assistant`, `042_Device_Control`. Depends on Phase 1's plugin
framework actually existing.

## Phase 9 — Operations & Release

`036_Backup_Restore`, `037_User_Profiles`, `043_Logging`, `044_Monitoring`,
`045_Performance`, `046_Offline_Mode`, `047_Update_Manager`,
`049_Documentation`, `050_Release_v1`. This phase is also where CI/CD
should grow into actual CD (image publishing, deployment automation — see
[docs/architecture/07_DEPLOYMENT.md](docs/architecture/07_DEPLOYMENT.md)'s
"Not yet implemented" section) and where `docs/guides/Release_Process.md`
(currently a stub) needs to be filled in for real.

## Explicitly not on this roadmap

Anything not listed in `docs/features/001`–`050` — don't add scope beyond
what's already specified without discussing it first.
