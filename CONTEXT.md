# Meeting Co-Pilot — Project Context & Brainstorm Summary

---

## What Is This Project?

You are building a **Meeting Co-Pilot** — an AI agent that listens to meeting recordings, understands what was discussed, and then automatically takes real actions like sending emails, creating calendar events, and assigning tasks.

You built this as a **demo prototype** for a pitch to **NEURA Robotics** (a robotics company in Metzingen, Germany). The consultancy you work for is **Futurice**, and you are trying to win NEURA as a client by showing them what real agentic AI automation looks like.

The contact at NEURA is **Kai Kölsch**, Head of CEO Office.

---

## The Tech Stack

| Thing | What it is |
|---|---|
| **n8n** | A visual workflow builder — you can see the whole agent logic as a diagram on screen |
| **AI Agent node** | The brain of the system — uses GPT-4o via OpenRouter |
| **Microsoft Graph API** | Connects to real Microsoft 365 — real emails, real calendar, real Teams |
| **Demo UI** | A web page at `localhost:8080/v3.html` — shows the approval panel |
| **Proxy** | `demo/proxy.py` — run with `python3 proxy.py` to make the UI talk to n8n |

---

## What You Have Already Built (v4 — Working ✅)

The full pipeline works end to end. Here's what happens when you upload a meeting recording:

1. Audio transcript comes in
2. The AI agent runs and uses **6 tools**:
   - `check_blocker_history` — checks if this person has had blockers before
   - `send_action_chat` — sends a Teams message to the person with their tasks
   - `draft_external_email` — writes a follow-up email for external participants
   - `check_calendar_availability` — checks real calendar before suggesting a meeting time
   - `schedule_followup_meeting` — creates an actual calendar event
   - `create_deadline_reminder` — sets a real reminder
3. If there were **external people** in the meeting, the agent **pauses and waits for a human to review** before sending anything outside
4. A **web UI** shows all the action items grouped by person — you can edit them before approving, and edits are passed through to n8n on approval
5. When you click **Approve**, everything gets sent: emails land in Outlook, calendar events get created, reminders are set
6. **Real Teams DMs** are sent via Microsoft Graph API to each task owner (not email stand-ins)

**Important detail about NEURA's setup:**
NEURA records their in-person meetings with a **physical voice recorder**, uploads the audio file, it gets transcribed, and then it's sent into this workflow. They don't just use Teams calls.

---


---

## Demo Credentials

- Everything goes to: `AncyJoseph@Fututrice.onmicrosoft.com` (note: sandbox domain is Fututrice not Futurice)
- M365 credential name: "Futurice M365"
- Workflow file: `workflows/neura_meeting_agent_v4_teams.json`

---

## What Makes This Different From Microsoft Copilot?

Microsoft Copilot (their built-in AI for Teams/M365) already does some things:
- Summarizes meetings
- Suggests tasks
- Takes meeting notes

**But Copilot cannot do these things:**
- Remember anything from past meetings — it resets to zero every time
- Send emails or take actions outside Microsoft
- Work with physical recorder uploads (only Teams calls)
- Track if the same problem keeps coming up across meetings
- Know who the external vs internal participants are
- Send external vendors a confirmation of what they promised

**Our agent does all of that.** That's the pitch.

---

## The NEURA Pitch Context

NEURA's Business AI Center is evaluating AI automation partners. They want to see:
- Real agentic behavior (not just a chatbot)
- Real M365 integration (not a toy)
- Something that solves problems their teams actually have

The meeting setup will likely be **hybrid** (some people in the room, some on Teams).

---

## Ideas We Brainstormed

A colleague (Finn's team) suggested two ideas:
1. **Do the demo live** during the actual hybrid pitch meeting instead of using a prepared transcript
2. **Add memory and reminders** so the agent can reference past meetings and send proactive nudges

You added: let's not just copy what exists — let's think about what the agent can genuinely do that no product does today. Agentic is the differentiator.

---

## The Live Demo Question

**Recommendation: Don't go fully live. Simulate live instead.**

Here's the approach:
- Record a 12–15 minute rehearsal call this week with your team
- Make the content relevant to NEURA (firmware timelines, a supplier who's been late, a safety certification topic)
- During the pitch: play that audio through a virtual audio device (BlackHole on Mac / VB-Cable on Windows)
- The transcription, AI agent, and all M365 actions run live in real time in front of the client

Everything is real — emails land, calendar events get created. The only thing controlled is the audio content, and that's actually better because you avoid awkward real-meeting noise.

**Risk of going fully live:** one mic failure or network spike in the room kills the demo completely. Not worth it in a competitive evaluation.

---

## Full Feature List (Simple Version)

### 1. The Agent Remembers Past Meetings
- Saves every decision with who said it and when
- Links all meetings where the same topic was discussed
- Catches contradictions (decided one thing last week, different thing this week)
- Lets you search "why did we choose X?" across all past transcripts
- Flags which decisions are risky to reverse

### 2. Making Sure Things Actually Get Done
- Auto-creates tasks in Planner with the right owner and deadline
- Catches tasks with no owner ("someone should check on that...")
- Notices when the same deadline gets missed and promised again
- After 3 meetings with the same unresolved blocker → drafts escalation for manager to approve
- Sends reminder to task owner before deadline, updates task based on their reply
- Tracks what external suppliers promised and sends them a confirmation email
- Scores how confident commitments sound ("I think we can..." vs "we will...")

### 3. Sending the Right Info to the Right People
- Generates a short non-technical summary for leadership (ready to forward, no editing)
- Sends external partners only their own tasks by email — no Teams login needed
- Handles mixed German/English meetings — one clean action list in both languages
- Privately tells the organizer if an important person said nothing during the meeting

### 4. Helping You Before the Meeting Starts
- Shows each attendee's open tasks and last meeting notes before the call
- Before a sprint standup or planning: auto-generates what's open, blocked, due
- Sends each person only what changed since the last meeting (not the whole history)
- 48 hours before a big meeting: full briefing on that contact's history and open commitments
- Background monitor: if a delivery date was mentioned in a meeting and nobody talks about it again in 5 days, sends a nudge

### 5. Hybrid Meeting Support
- **Handles physical recorder uploads** — watches for uploaded audio files, processes them exactly like a Teams call (already built — this is huge)
- Catches decisions being made in real time and posts them in chat for instant confirmation
- Quietly tells the organizer if remote participants kept getting cut off
- Sends a private message to a quiet expert: "they just decided something in your area, do you want to weigh in?"

### 6. Legal, Safety & Compliance (Important for German Robotics)
- Auto-tags anything safety-related (ISO, CE marking, functional safety, SIL) and saves a traceable record exportable as PDF
- Flags "it's out of tolerance but we'll handle it later" and asks engineer to open a quality report
- Handles GDPR consent before recording — who agreed, when, deletion schedule
- Works Council mode (Betriebsrat) — turns off individual speaker tracking to be compliant with German labor law (BetrVG §87)
- Full audit log of every task reassignment and escalation — exportable
- When an engineering change is agreed, immediately asks: does this affect CE marking? Safety functions? Logs the answer.
- On-demand report of all compliance decisions across all meetings, grouped by standard

### 7. Big Picture Insights Across All Meetings
- Supplier risk: if 3 teams have been mentioning the same supplier with worried language, surfaces it before anyone formally escalates
- Hidden gap detector: Team A assumed Team B would deliver something — but Team B never confirmed it in any meeting
- How long does a problem take to reach leadership? Flags things getting stuck at team level
- Spots people who rarely speak but whose contributions consistently unblock things

### 8. Connecting to Other Tools
- Smarter Planner task creation — right bucket, right sprint, inferred from context
- Adds risks mentioned in meetings directly to your risk register spreadsheet
- Updates your RACI/responsibility matrix when ownership changes in a meeting
- Culture-aware: "Das sollte machbar sein" and "we will deliver" sound similar but mean different things in terms of certainty — the agent knows the difference
- At project milestones: generates full audit package of all decisions, alternatives considered, who approved

---

## Top 5 Features to Lead With in the Pitch

### 1. Physical Recording Support *(already built)*
NEURA uses a physical recorder for in-person meetings. Our agent handles that automatically. Microsoft Copilot only works on Teams calls — every in-person meeting NEURA has is invisible to Copilot. This one feature alone makes the product relevant to how they actually work.

**Pitch line:** *"Copilot only works when Microsoft is in the room. We work wherever the meeting happens."*

---

### 2. Decision Memory + Contradiction Detection
Every decision is saved with who said it and when. If the team contradicts a past decision, the agent catches it. For an engineering team building robots, "I thought we agreed on the 48V motor" is a real problem that costs real time.

**Pitch line:** *"Copilot forgets everything after each meeting. We remember everything."*

---

### 3. Vendor Commitment Tracker + Auto Confirmation Email
After any meeting with a supplier, the agent automatically emails them: "here's what you committed to, please confirm." No manual work. Hardware companies live and die by supplier commitments. Copilot doesn't even know external people were in the meeting.

**Pitch line:** *"When a supplier makes a promise in your meeting, we send them a written confirmation before they've left the call."*

---

### 4. Safety & Compliance Tracker *(important for German robotics)*
The agent auto-tags anything related to ISO, CE marking, or functional safety, saves a traceable record, and can generate a PDF report for audits. It also comes with GDPR consent management and a Works Council mode — which is specifically required by German labor law. No other meeting AI product has this.

**Pitch line:** *"Built for German enterprise. GDPR-compliant, Betriebsrat-compatible, audit-ready."*

---

### 5. Recurring Problem Escalator
The same blocker comes up in 3 meetings, nothing changes, nobody escalates because it's awkward. The agent drafts the escalation message and hands it to the manager to approve with one click. It removes the social friction that delays hard conversations.

**Pitch line:** *"The agent doesn't just track blockers — it escalates them for you, when you've waited long enough."*

---

## The Core Pitch (One Paragraph)

> Microsoft Copilot summarizes each meeting and closes. It forgets everything, ignores in-person meetings, and stops at creating a Planner task. Our agent keeps the commitment loop open — it remembers across meetings, acts across systems, follows up with suppliers, escalates blockers, and is compliant with German enterprise requirements. It doesn't just help you understand what happened in a meeting. It makes sure what was said actually happens.
