---
name: ig-growth
description: Run the Instagram growth team for the creator's personal travel account. Use when the user says "/ig-growth", asks to plan the week's Instagram posts, draft posts, review analytics, or work on growing their Instagram.
---

# Instagram growth team

Coordinate these subagents (in `.claude/agents/`) using the shared workspace in `instagram/`:

| Agent | Role | Writes |
|---|---|---|
| ig-trend-scout | Trends, formats, hashtags, comparable creators | `instagram/research/` |
| ig-growth-analyst | Reads Insights exports, reports what worked | `instagram/insights/` |
| ig-strategist | Positioning, pillars, weekly calendar | `instagram/content-calendar.md` |
| ig-content-creator | Reel scripts, carousels, captions | `instagram/drafts/` |
| ig-editor | Quality + fact check, marks ready | edits drafts |
| ig-community-manager | Replies, engagement list, collab pitches | `instagram/drafts/outreach-*` |

## Step 0 — onboarding (first run only)
If `instagram/profile.md` still has blank fields, interview the user to fill it in (a few questions at a time), then have **ig-strategist** propose positioning, pillars, bio and cadence. Get the user's sign-off before planning posts.

## Weekly loop (default when the user just says "run the team")
1. In parallel: **ig-trend-scout** (fresh research) and, if new files are in `instagram/insights/`, **ig-growth-analyst**.
2. **ig-strategist** writes next week's rows in `instagram/content-calendar.md`.
3. Show the user the plan; adjust on feedback.
4. **ig-content-creator** drafts each approved row (can run several in parallel, one per post).
5. **ig-editor** reviews all drafts.
6. **ig-community-manager** prepares the engagement list and any collab pitches.
7. Summarise for the user: what's ready to post, what needs their input (photos to pick, `[CHECK]` facts), and what to export from Insights next week.

## Ad-hoc requests
Route single asks straight to one agent (e.g. "write a caption for my Kyoto photos" → ig-content-creator then ig-editor).

## Ground rules for the whole team
- The team drafts; the user posts, replies and sends. No automation against Instagram's terms, no bought followers, no engagement pods.
- No invented facts or stats; unverified items are marked `[CHECK]`.
- Protect the user's privacy: no real-time location sharing, no home details.
