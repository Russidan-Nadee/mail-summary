---
name: gmail-daily-briefing
description: Fetch Gmail emails from the last 24h, rank by importance, summarize into bullet points, and auto-create Google Calendar events for detected meetings.
metadata:
  openclaw:
    requires:
      bins:
        - python
      files:
        - token.json
---

# Email & Calendar Assistant Skill

## Description
This skill reads Gmail emails, ranks them by importance, summarizes each email into bullet points, and creates Google Calendar events if an email contains a meeting or interview that is not already on the calendar.

## Capabilities
- Read emails (read-only)
- Rank emails by importance
- Summarize emails into bullet points
- Detect meeting/interview emails
- Create Google Calendar events (only when not already added)

## Scripts
- `python scripts/fetch_emails.py` — Fetch emails from the last 24 hours and print full content
- `python scripts/create_event.py --title "..." --date "YYYY-MM-DD" --time "HH:MM" [--duration 60]` — Create a Google Calendar event
- `python scripts/setup_auth.py` — Generate Google OAuth URL (Step 1 of auth setup)
- `python scripts/setup_auth.py --callback "<URL>"` — Complete auth and save token.json (Step 2 of auth setup)

## Auth Setup (First-Time Only)

This skill requires a `token.json` file to access Gmail and Google Calendar on behalf of the user.
If `token.json` does not exist, the agent MUST complete the following setup before running any other script.

### When the user sends a `client_secret_*.json` file:

1. Write the file content to the project root as `client_secret_*.json` (preserve the original filename). The user sends this as an attachment — the agent must create the file in the project root directory before running any script.
2. Run: `python scripts/setup_auth.py`
3. Send the printed URL to the user as a clickable markdown link, with this message:
   > "Please open this link in your browser and authorize access. After you approve, your browser will redirect to a localhost page that shows an error — that's expected. Copy the full URL from the browser address bar and send it back to me."
   > [Click here to authorize](PASTE_AUTH_URL_HERE)
4. Wait for the user to send back the redirect URL (starts with `http://localhost/?...`)
5. Run: `python scripts/setup_auth.py --callback "<the URL the user sent>"`
6. Confirm to the user: "Auth complete. I can now access your Gmail and Google Calendar."

### Notes
- The redirect URL will look like: `http://localhost/?state=...&code=...&scope=...`
- The "error" page the user sees is normal — it just means no server is running at localhost, which is expected
- Once `token.json` is saved, the agent auto-refreshes it when expired — no need to repeat setup

## Input
- User request (e.g., "Summarize today's important emails")

## Output to User
For each email (sorted by importance, most important first):
```
#1
From: <sender>
Subject: <subject>
- bullet point summary
- bullet point summary
[📅 Calendar event created: <title> on <date> at <time>]  ← only if applicable
```

## Behavior
1. Run `fetch_emails.py` to get emails from the last 24 hours
2. Read and analyze all emails
3. Rank emails by importance internally (1 = most important) — do not show ranking logic to user
4. Summarize each email into bullet points
5. If a meeting or interview is detected in an email:
   - Check if the event already exists on Google Calendar (e.g., from a Google Calendar invite)
   - If the event does NOT exist yet, run `create_event.py` to create it
   - If the event already exists, skip — do not create a duplicate

## Notes
- Gmail and Google Calendar API required
- Can be triggered by user request or external scheduler (e.g., cron job)
- Date must be in `YYYY-MM-DD` format, time in `HH:MM` format when calling `create_event.py`