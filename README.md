# NEURA Meeting Intelligence — n8n Prototype

> Agentic meeting automation prototype built for the NEURA Robotics RFI response.  
> Developed by **Futurice** using n8n (self-hosted) + GPT-4o via OpenRouter + Microsoft Graph API.

---

## What it does

1. **Reads a meeting transcript** (hardcoded demo or real Teams transcript)
2. **Extracts structured data** — action items with owners, deadlines, priorities, dependencies
3. **Checks a simulated blocker history** — flags recurring issues across sprints
4. **Detects external participants** — triggers Human-in-the-Loop approval if external contacts are present
5. **Sends personalised action item emails** — one per owner, via Microsoft Graph API (`/me/sendMail`)
6. **Creates a Teams follow-up meeting** — via `/me/onlineMeetings` + `/me/calendar/events`, with join link embedded

---

## Workflows

| File | Description |
|------|-------------|
| `workflows/neura_meeting_agent_v1_demo.json` | Original demo — all tools simulated (mock responses, no real API calls) |
| `workflows/neura_meeting_agent_v2_live_m365.json` | Live M365 — real Graph API calls for email and calendar |

---

## Tech Stack

| Component | Detail |
|-----------|--------|
| Orchestration | n8n self-hosted (Node 20) |
| LLM | GPT-4o via OpenRouter |
| Email & Calendar | Microsoft Graph API (OAuth2) |
| Auth | Azure App Registration (Fututrice.onmicrosoft.com) |

---

## Setup

### 1. Prerequisites

- n8n self-hosted running: `PATH="/opt/homebrew/opt/node@20/bin:$PATH" n8n start`
- Node.js 20 via Homebrew
- An Azure App Registration with these Graph API permissions (admin consent granted):
  - `Mail.Send`
  - `Calendars.ReadWrite`
  - `OnlineMeetings.ReadWrite`
  - `User.Read`

### 2. Credentials

Copy `credentials.env.example` to `credentials.env` and fill in your values:

```bash
cp credentials.env.example credentials.env
```

### 3. n8n Credentials to create

| Name | Type | Details |
|------|------|---------|
| `OpenRouter` | OpenAI API | Base URL: `https://openrouter.ai/api/v1`, Key from OpenRouter |
| `Futurice M365` | Microsoft OAuth2 API | Client ID + Secret from Azure, tenant-specific auth URLs |

**Microsoft OAuth2 Credential URLs:**
```
Authorization URL: https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize
Access Token URL:  https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token
Scope: https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/User.Read https://graph.microsoft.com/OnlineMeetings.ReadWrite offline_access
```

### 4. Import workflow

In n8n: **Workflows → Import from file** → select `workflows/neura_meeting_agent_v2_live_m365.json`

After import, open `Create Teams Online Meeting` and `Create Calendar Event` and `Send Action Emails` nodes — select the **Futurice M365** credential in each.

---

## Demo flow

```
Run Demo
  └── Sample Meeting Data (hardcoded Robot Arm Integration Sync transcript)
        └── Meeting Agent (GPT-4o)
              ├── check_blocker_history   → simulated history lookup
              ├── send_action_email ×N    → drafts queued
              └── schedule_followup_meeting → meeting details queued
                    └── Parse Agent Output
                          ├── Email Drafts          (view-only preview)
                          ├── Split Action Items
                          │     └── Send Action Emails   → real /me/sendMail
                          ├── Create Teams Online Meeting → real /me/onlineMeetings
                          │     └── Create Calendar Event  → real /me/calendar/events
                          └── External Participants?
                                ├── TRUE → Approval Required → Wait → Approved?
                                └── FALSE → Auto-Executed (Internal)
```

All emails and calendar invites are routed to `AncyJoseph@Fututrice.onmicrosoft.com` for demo purposes.

---

## Human-in-the-Loop

When external participants are detected (e.g. Thomas Becker from Bosch), the workflow pauses and outputs a `resume_url`. Open that URL in a browser to approve or reject distribution.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create_doc.py` | Regenerates the Word prototype documentation |

---

## Documents

| File | Description |
|------|-------------|
| `docs/NEURA_Meeting_Agent_Prototype.docx` | Full prototype write-up for the RFI response |
| `docs/NEURA_RFI_English.docx` | Original NEURA Robotics RFI (English) |
