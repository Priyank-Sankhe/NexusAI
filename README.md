# NexusAI 🧠
Your personal AI study operating system — built by a developer, for a developer.

## Live Demo
[NexusAI](https://nexusai-gcovifrsl5ovpxcse5gun4.streamlit.app/)

## The Problem
I'm a career switcher learning software development at Scaler Academy.
I was losing study time to three specific problems:
- Hitting Claude's token limits mid-session and waiting hours to continue
- Consuming lectures passively without actually retaining anything
- Losing entire days with no system to catch and recover from deviation

I built NexusAI to fix all three — and I use it every single day.

## What It Does
Five integrated modes, one shared persistent data layer:

### 💬 Study Chat
AI study assistant powered by Groq/Llama3. No token limits, no waiting.
Pre-loaded with curriculum context so you never re-explain your situation.

### 🎯 GapFinder
- Generates DSA problems by topic on demand
- Evaluates your solution strictly and honestly
- Flags weak topics automatically with a score (0/1/2)
- Resurfaces weak topics for retest after 7 days using spaced repetition

### ⚡ FlowState
- Builds a specific hour-by-hour daily study plan (3PM–11PM window)
- Pulls weak topics from GapFinder and schedules retest time automatically
- 7PM check-in detects deviation and replans the rest of the day instantly
- 11PM end-of-day log gives honest completion assessment and tomorrow's focus

### 📊 Dashboard
- Problems attempted, marked solid, flagged weak — live counters
- Weak topic list with days since last attempt and retest countdown
- Topic performance scores across all attempts
- Recent day logs with completion reviews

### 🎤 Mock Interview
- Generates role-specific technical interview questions by topic and difficulty
- Built-in timer to track solution time against the 20-minute interview bar
- Evaluates answers at the actual hiring bar — Strong Hire, Hire, or No Hire
- Tells you exactly what a hired candidate would say for your weakest answer

## What Makes It Different From Just Using ChatGPT
- **Persistent memory** — data survives every session, reload, and redeploy
- **Spaced repetition logic** — knows what you're most likely to have forgotten
- **Cross-tab intelligence** — FlowState automatically knows your GapFinder weak spots
- **No token walls** — Groq's free tier handles unlimited daily usage
- **Purpose-built context** — responds as a study mentor, not a general assistant
- **Hiring-bar evaluation** — Mock Interview judges you the way a real interviewer would, not just correct/incorrect

## Tech Stack
- Python
- Streamlit
- Groq API (Llama 3.1 8b Instant)
- JSONBin (persistent key-value storage)
- Streamlit Community Cloud (deployment)
- GitHub (version control)

## Version Roadmap
- ✅ V1: Study Chat + GapFinder + FlowState (core loop)
- ✅ V2: Persistent storage + spaced repetition + cross-tab data sharing
- ✅ V3: Dashboard — progress tracking, weak topic list, day log history
- ✅ V4: Mock Interview — hiring-bar evaluation with timer and verdict
- ⬜ V5: Streak tracking + consistency analytics
- ⬜ V6: React frontend rebuild (post-LLD modules)

## Why I Built This
Every feature in NexusAI exists because I personally needed it.
The token limit problem was real. The retention problem was real.
The lost days were real. This tool is the solution I built for myself —
and it gets more useful every day I use it.

## Author
Shivang — career switcher, Scaler Academy Software Development Program
Building in public.
