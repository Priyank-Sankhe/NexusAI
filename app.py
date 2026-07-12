import streamlit as st
from groq import Groq
from datetime import datetime, date
from zoneinfo import ZoneInfo
import requests
import re
import logging

# Configure basic logging for background error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusAI")

st.set_page_config(page_title="NexusAI", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp {
    background:
        radial-gradient(circle at 0% 0%, rgba(138,90,54,.18), transparent 30%),
        radial-gradient(circle at 100% 100%, rgba(91,58,38,.18), transparent 35%),
        linear-gradient(135deg, #16110D 0%, #211711 35%, #2B1E17 65%, #35241B 100%);
    color:#F5F1EC;
    font-family:'Inter',sans-serif;
}

.stApp::before {
    content:"";
    position:fixed;
    inset:0;
    background: radial-gradient(rgba(255,255,255,.04) 2px, transparent 2px);
    background-size:42px 42px;
    opacity:.25;
    filter:blur(2px);
    pointer-events:none;
    z-index:-1;
}

.block-container {
    max-width:1280px;
    padding-top:1.8rem !important;
    padding-bottom:2rem !important;
    padding-left:2rem !important;
    padding-right:2rem !important;
}

h1 { color:#FFF4E8; font-weight:800; letter-spacing:.5px; }
h2 { color:#F7E6D5; font-weight:700; }
h3 { color:#F4DDC8; }
h4 { color:#EBD5BF; }

[data-testid="metric-container"] {
    background: linear-gradient(180deg, rgba(67,47,34,.78), rgba(48,33,24,.72));
    border:1px solid rgba(255,255,255,.06);
    border-radius:18px;
    padding:20px;
    backdrop-filter:blur(14px);
    box-shadow: 0 10px 30px rgba(0,0,0,.35), inset 0 1px rgba(255,255,255,.05);
    transition:.25s;
}
[data-testid="metric-container"]:hover {
    transform:translateY(-3px);
    border-color:rgba(196,145,92,.35);
    box-shadow: 0 15px 40px rgba(0,0,0,.45);
}

.stButton>button {
    width:100%;
    border:none;
    border-radius:14px;
    padding:.7rem;
    font-weight:700;
    color:white;
    background: linear-gradient(135deg, #8A5A36, #B77A48);
    transition:.25s;
}
.stButton>button:hover {
    transform:translateY(-2px);
    background: linear-gradient(135deg, #B77A48, #D9985C);
    box-shadow: 0 12px 28px rgba(0,0,0,.35);
}

.stTextInput input {
    background:#2A2019 !important;
    color:white !important;
    border-radius:12px !important;
    border:1px solid rgba(255,255,255,.08) !important;
}
.stTextArea textarea {
    background:#2A2019 !important;
    color:white !important;
    border-radius:14px !important;
    border:1px solid rgba(255,255,255,.08) !important;
}

.stSelectbox div[data-baseweb="select"] {
    background:#2A2019;
    border-radius:12px;
}

.stSlider { padding-top:12px; }

.stTabs [role="tablist"] { gap:12px; margin-bottom:20px; }
.stTabs [role="tab"] {
    background:#2C1F17;
    color:#D7C5B6;
    border-radius:12px;
    padding:12px 22px;
    transition:.25s;
    font-weight:600;
}
.stTabs [role="tab"]:hover { background:#5A3A27; color:white; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #8A5A36, #B77A48) !important;
    color:white !important;
}

[data-testid="stChatMessage"] {
    background: rgba(59,42,30,.62);
    border-radius:18px;
    border:1px solid rgba(255,255,255,.05);
    padding:18px;
    margin-bottom:14px;
}

.stSuccess { border-radius:12px; }
.stWarning { border-radius:12px; }
.stError { border-radius:12px; }
.stInfo { border-radius:12px; }

.streamlit-expanderHeader { background:#2C2018; border-radius:10px; }

hr { border:none; height:1px; background:rgba(255,255,255,.08); }

::-webkit-scrollbar { width:10px; }
::-webkit-scrollbar-track { background:#1A1411; }
::-webkit-scrollbar-thumb { background:#7B5235; border-radius:20px; }
::-webkit-scrollbar-thumb:hover { background:#AE7546; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #20150F, #2D1E16);
    border-right:1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] .block-container { padding-top:1.8rem; }
section[data-testid="stSidebar"] h2 { color:#FFF3E6; }
section[data-testid="stSidebar"] .stButton>button {
    background:#3B291E;
    border-radius:12px;
    margin-bottom:8px;
}
section[data-testid="stSidebar"] .stButton>button:hover { background:#7D5436; }

.stAlert { border-radius:16px; border:none; box-shadow:0 8px 20px rgba(0,0,0,.18); }
</style>
""", unsafe_allow_html=True)

# ==================== CONFIG ====================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    MASTER_KEY = st.secrets["JSONBIN_MASTER_KEY"]
    JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
except KeyError as e:
    st.error(f"⚠️ Missing secret configuration: {e}. Please check your `.streamlit/secrets.toml` file.")
    st.stop()

MISSION_PENDING = "pending"
MISSION_ACTIVE = "active"
MISSION_COMPLETED = "completed"
MISSION_SKIPPED = "skipped"

# ==================== HELPERS & SAFE PARSERS ====================
def parse_date_safe(date_str, fmt="%Y-%m-%d"):
    """Safely parse a date string, returning today's date if malformed."""
    if not date_str:
        return datetime.now().date()
    try:
        if len(date_str) > 10 and fmt == "%Y-%m-%d":
            date_str = date_str[:10]
        return datetime.strptime(str(date_str), fmt).date()
    except (ValueError, TypeError):
        return datetime.now().date()

def parse_datetime_safe(dt_str, fmt="%Y-%m-%d %H:%M:%S"):
    """Safely parse a datetime string, returning current datetime if malformed."""
    if not dt_str:
        return datetime.now()
    try:
        return datetime.strptime(str(dt_str), fmt)
    except (ValueError, TypeError):
        return datetime.now()

# ==================== STORAGE ====================
def load_data():
    default_db = {
        "gap_log": [],
        "day_logs": [],
        "missions": [],
        "current_mission": None
    }
    try:
        response = requests.get(JSONBIN_URL, headers={"X-Master-Key": MASTER_KEY}, timeout=10)
        response.raise_for_status()
        data = response.json().get("record", {})
        for key, value in default_db.items():
            if not isinstance(data.get(key), type(value)):
                data[key] = value
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to load cloud data: {e}")
        # Return existing session state db if offline to prevent silent wipe
        if "db" in st.session_state and isinstance(st.session_state.db, dict):
            return st.session_state.db
        return default_db
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        return default_db

def save_data(data):
    try:
        response = requests.put(
            JSONBIN_URL,
            headers={"X-Master-Key": MASTER_KEY, "Content-Type": "application/json"},
            json=data,
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Cloud sync failed: {e}")
        st.toast("⚠️ Cloud sync failed. Progress saved locally for this session.")
    except Exception as e:
        logger.error(f"Unexpected error saving data: {e}")

def get_weak_topics(gap_log):
    weak = []
    today = datetime.now().date()
    if not isinstance(gap_log, list):
        return weak
    for entry in gap_log:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") == "gap_entry":
            score = entry.get("score", 2)
            entry_date = parse_date_safe(entry.get("date", ""))
            days_since = (today - entry_date).days
            if score <= 1 and days_since >= 7:
                weak.append({
                    "topic": entry.get("topic", "General"),
                    "days_since": days_since,
                    "score": score
                })
    return weak

def create_mission(title, reason, priority, duration):
    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "title": title,
        "reason": reason,
        "priority": priority,
        "duration": max(1, int(duration)),
        "status": MISSION_PENDING,
        "progress": 0,
        "started_at": None,
        "completed_at": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_daily_mission():
    weak_topics = get_weak_topics(st.session_state.db.get("gap_log", []))
    if not weak_topics:
        return create_mission(
            title="Complete Today's Scaler Session",
            reason="No weak topics detected yet — keep solving problems.",
            priority=100,
            duration=60
        )
    weakest = sorted(weak_topics, key=lambda x: x.get("days_since", 0), reverse=True)[0]
    return create_mission(
        title=f"Revise {weakest['topic']}",
        reason=f"Last revised {weakest['days_since']} days ago — overdue for retest.",
        priority=100,
        duration=25
    )

def section_header(icon, title, subtitle, accent):
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{accent},#2A2019);
        padding:22px;
        border-radius:18px;
        margin-bottom:20px;
        border-left:6px solid #D9A066;
        box-shadow:0 10px 25px rgba(0,0,0,.25);
    ">
        <h2 style="margin:0;color:white;">{icon} {title}</h2>
        <p style="margin-top:8px;color:#E6D7C8;font-size:15px;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if "db" not in st.session_state or not isinstance(st.session_state.db, dict):
    st.session_state.db = load_data()
if "messages" not in st.session_state or not isinstance(st.session_state.messages, list):
    st.session_state.messages = []
if "flow_plan" not in st.session_state:
    st.session_state.flow_plan = None
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "brain" not in st.session_state or not isinstance(st.session_state.brain, dict):
    st.session_state.brain = {
        "current_focus": None,
        "current_module": None,
        "recommended_action": None,
        "recommended_topic": None,
        "last_activity": None,
        "learning_mode": "normal",
        "streak": 0,
        "energy": "unknown"
    }

# Ensure core DB lists exist
for k in ["gap_log", "day_logs", "missions"]:
    if k not in st.session_state.db or not isinstance(st.session_state.db[k], list):
        st.session_state.db[k] = []

# ==================== MISSION ENGINE ====================
def update_recommended_topic():
    weak_topics = get_weak_topics(st.session_state.db.get("gap_log", []))
    if weak_topics:
        weakest = sorted(weak_topics, key=lambda x: x.get("days_since", 0), reverse=True)[0]
        st.session_state.brain["recommended_topic"] = weakest["topic"]
    else:
        st.session_state.brain["recommended_topic"] = None

update_recommended_topic()

if st.session_state.db.get("current_mission") is None:
    mission = generate_daily_mission()
    if mission:
        st.session_state.db["missions"].append(mission)
        st.session_state.db["current_mission"] = mission
        st.session_state.brain["current_focus"] = mission["title"]
        st.session_state.brain["recommended_action"] = "Start Mission"
        save_data(st.session_state.db)

mission = st.session_state.db.get("current_mission")
if isinstance(mission, dict):
    mission.setdefault("progress", 0)
    mission.setdefault("duration", 25)
    mission.setdefault("status", MISSION_PENDING)
    mission.setdefault("reason", "")
    mission.setdefault("started_at", None)
    mission.setdefault("completed_at", None)
else:
    mission = None

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🧠 NexusAI")
    st.caption("AI Software Engineering Coach")
    st.divider()

    gap_log_s = st.session_state.db.get("gap_log", [])
    day_logs_s = st.session_state.db.get("day_logs", [])

    st.metric("📚 Problems", len([e for e in gap_log_s if isinstance(e, dict) and e.get("type") == "gap_entry"]))
    st.metric("🎯 Weak Topics", len({e.get("topic") for e in gap_log_s if isinstance(e, dict) and e.get("type") == "gap_entry" and e.get("score", 0) <= 1 and e.get("topic")}))
    st.metric("📅 Study Days", len(day_logs_s))

    st.divider()
    st.markdown("### 🚀 Today's Goal")
    st.progress(0.60)
    st.caption("Complete today's Scaler session")
    st.divider()

    st.markdown("### ⚡ Quick Actions")
    st.button("💬 Study Chat", use_container_width=True)
    st.button("🎯 GapFinder", use_container_width=True)
    st.button("🎤 Mock Interview", use_container_width=True)
    st.button("📊 Dashboard", use_container_width=True)
    st.divider()
    st.caption("NexusAI v1.0 (Hardened)")

# ==================== HERO ====================
try:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
except Exception:
    now = datetime.now()

hour = now.hour
today_name = now.strftime("%A")

if hour < 12:
    greeting = "Good Morning ☀️"
elif hour < 17:
    greeting = "Good Afternoon 🌤️"
else:
    greeting = "Good Evening 🌙"

gap_log_h = st.session_state.db.get("gap_log", [])
day_logs_h = st.session_state.db.get("day_logs", [])
problem_count = len([e for e in gap_log_h if isinstance(e, dict) and e.get("type") == "gap_entry"])
weak_count = len({e.get("topic") for e in gap_log_h if isinstance(e, dict) and e.get("type") == "gap_entry" and e.get("score", 0) <= 1 and e.get("topic")})
day_count = len(day_logs_h)

hero = st.container(border=True)
with hero:
    left, right = st.columns([4, 1])
    with left:
        st.title("🧠 NexusAI")
        st.subheader(greeting)
        st.write("### Ready to continue your Software Engineering journey?")
        st.caption("Every coding session brings you closer to becoming a Software Engineer.")
    with right:
        st.markdown(f"### 📅 {today_name}")

st.write("")

a, b, c = st.columns(3)
with a:
    st.metric("📚 Problems Solved", problem_count)
with b:
    st.metric("🎯 Weak Topics", weak_count)
with c:
    st.metric("📅 Study Days", day_count)

st.write("")

# ==================== AI RECOMMENDATION ====================
brain = st.session_state.brain
recommended_topic = brain.get("recommended_topic")

if recommended_topic:
    recommendation = (
        f"🧠 NexusAI Recommendation\n\n"
        f"Your highest priority right now is **{recommended_topic}**.\n"
        f"Strengthen this topic before moving on."
    )
elif brain.get("current_focus"):
    recommendation = (
        f"🎯 Continue working on **{brain['current_focus']}**."
    )
elif mission and mission.get("status") == MISSION_PENDING:
    recommendation = (
        f"🚀 Start today's mission: **{mission.get('title', 'Daily Task')}**."
    )
else:
    recommendation = (
        "💡 Generate a new GapFinder problem to keep improving."
    )

st.info(recommendation)

if recommended_topic:
    if st.button(
        f"🎯 Practice {recommended_topic}",
        key="practice_recommended_topic",
        use_container_width=True
    ):
        st.session_state.brain["current_focus"] = recommended_topic
        st.success(f"{recommended_topic} is now your active focus.")
        st.rerun()
elif mission and mission.get("status") == MISSION_PENDING:
    if st.button(
        "🚀 Start Current Mission",
        key="hero_start_mission",
        use_container_width=True
    ):
        mission["status"] = MISSION_ACTIVE
        mission["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data(st.session_state.db)
        st.rerun()

# ==================== CURRENT MISSION ====================
st.markdown("## 🎯 Current Mission")
mission = st.session_state.db.get("current_mission")
mission_card = st.container(border=True)

with mission_card:
    if isinstance(mission, dict):
        left, right = st.columns([3, 1])
        with left:
            st.subheader(mission.get("title", "Untitled Mission"))
            priority = mission.get("priority", 100)
            if priority >= 90:
                st.success("🔥 High Priority")
            elif priority >= 60:
                st.warning("⚡ Medium Priority")
            else:
                st.info("📌 Low Priority")

            st.caption(mission.get("reason", ""))

            if mission.get("status") == MISSION_ACTIVE and mission.get("started_at"):
                started = parse_datetime_safe(mission["started_at"])
                elapsed_seconds = (datetime.now() - started).total_seconds()
                total_seconds = max(1, mission.get("duration", 25) * 60)
                progress = min(100, max(0, int((elapsed_seconds / total_seconds) * 100)))
                mission["progress"] = progress

            progress_val = min(1.0, max(0.0, mission.get("progress", 0) / 100.0))
            st.progress(progress_val)
            st.caption(f"Progress: {mission.get('progress', 0)}%")

        with right:
            st.metric("Duration", f"{mission.get('duration', 25)} min")
            st.metric("Status", str(mission.get("status", "unknown")).title())

            if mission.get("status") == MISSION_PENDING:
                if st.button("▶ Start Mission", key="start_mission_btn", use_container_width=True):
                    mission["status"] = MISSION_ACTIVE
                    mission["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(st.session_state.db)
                    st.rerun()

            if mission.get("status") == MISSION_ACTIVE:
                if st.button("✅ Complete Mission", key="complete_mission_btn", use_container_width=True):
                    mission["status"] = MISSION_COMPLETED
                    mission["progress"] = 100
                    mission["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.db["current_mission"] = None
                    save_data(st.session_state.db)
                    st.rerun()
    else:
        st.info("No active mission yet. Solve problems in GapFinder to generate one.")

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Study Chat", "🎯 GapFinder", "⚡ FlowState", "📊 Dashboard", "🎤 Mock Interview"
])

# ==================== TAB 1 ====================
with tab1:
    st.session_state.brain["current_module"] = "Study Chat"
    section_header("💬", "Study Chat", "Ask anything about your Scaler journey. NexusAI remembers your learning context.", "#385C7A")

    for msg in st.session_state.messages:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Ask anything...")

    if user_input:
        st.session_state.brain["last_activity"] = "Asked a study question"
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        brain = st.session_state.brain
        brain_context = f"""
CURRENT AI STATE
Current Focus: {brain.get("current_focus")}
Recommended Topic: {brain.get("recommended_topic")}
Current Module: {brain.get("current_module")}
Last Activity: {brain.get("last_activity")}
"""
        system_context = brain_context + """You are NexusAI, a specialized software engineering study assistant.
STUDENT PROFILE:
- Name: Shivang
- Program: Scaler Academy Software Development Program
- Current module: Module 5 (AI & Agents)
- Completed: Java basics, intermediate DSA (arrays, prefix sum, carry forward, 
  contribution technique, sliding window, bit manipulation, 2D matrices, strings)
- Background: Career switcher, non-CS degree, learning from scratch
- Target: 18 LPA software development role
- Known weak areas: sliding window, contribution technique (not yet cold-solved)
TEACHING RULES:
1. Never give the answer immediately. Ask what the student already knows first.
2. Use first principles. Explain WHY before HOW.
3. When explaining algorithms: give intuition first, then example, then code.
4. When the student is wrong: identify the exact error precisely.
5. Use execution traces and concrete examples always.
6. After every explanation, ask one question to verify understanding.
7. If asked for code directly: give pseudocode first, real code second.
8. For DSA problems: brute force first, then optimize.
9. Never sugarcoat. If understanding is shallow, say so directly.
RESPONSE FORMAT:
- Concise and focused — no padding
- Bold key terms on first use
- End complex explanations with a verification question
SCOPE: Only answer questions about software engineering, DSA, Java, Python, 
system design, Scaler curriculum, career strategy, and AI/ML from Module 5.
Redirect anything outside this scope."""

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": system_context},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"⚠️ AI Inference error: {str(e)}. Please check your network or Groq API limits.")

# ==================== TAB 2 ====================
with tab2:
    st.session_state.brain["current_module"] = "GapFinder"
    section_header("🎯", "GapFinder", "Identify weak concepts and automatically generate targeted practice.", "#7A5636")
    st.caption("Get a problem, solve it, get evaluated. Weakness tracked automatically.")

    weak_topics = get_weak_topics(st.session_state.db.get("gap_log", []))
    if weak_topics:
        st.warning(f"⚠️ Topics due for retest: {', '.join(sorted(list({w['topic'] for w in weak_topics if 'topic' in w})))}")

    topics = ["Prefix Sum", "Sliding Window", "Contribution Technique",
              "Bit Manipulation", "2D Matrices", "Strings"]

    recommended = st.session_state.brain.get("recommended_topic")
    default_index = 0
    if recommended in topics:
        default_index = topics.index(recommended)

    selected_topic = st.selectbox(
        "Select a topic:",
        topics,
        index=default_index,
        key="gap_topic"
    )

    if st.button("Generate Problem", key="gen_problem"):
        st.session_state.brain["current_focus"] = selected_topic
        st.session_state.brain["last_activity"] = "Generated a practice problem"
        with st.spinner("Generating problem..."):
            problem_prompt = f"""Generate a DSA problem specifically and only on: {selected_topic}.
Format exactly like this:
PROBLEM: [clear problem statement with example input and output]
DIFFICULTY: [Easy/Medium]
HINT: [one line hint, not the solution]"""
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"You are a DSA problem generator. Only generate problems about {selected_topic}."},
                        {"role": "user", "content": problem_prompt}
                    ]
                )
                st.session_state.current_problem = response.choices[0].message.content
                st.session_state.current_topic = selected_topic
            except Exception as e:
                st.error(f"⚠️ Could not generate problem: {str(e)}")

    if "current_problem" in st.session_state and st.session_state.current_problem:
        st.markdown("### Problem")
        st.markdown(st.session_state.current_problem)

        user_solution = st.text_area(
            "Write your approach — pseudocode, logic, or actual code:",
            height=200,
            key="solution_input"
        )

        if st.button("Evaluate My Solution", key="eval_solution"):
            if len(user_solution.strip()) < 10:
                st.warning("Write an actual solution attempt before evaluating.")
            else:
                with st.spinner("Evaluating..."):
                    eval_prompt = f"""Problem: {st.session_state.current_problem}

Student's solution: {user_solution}

Evaluate strictly:
1. CORRECT: What did they get right?
2. MISSING: What's wrong or missing?
3. OPTIMAL SOLUTION: Show the correct approach
4. SCORE: 0 (wrong), 1 (partial), 2 (correct) — number only on this line formatted as 'SCORE: X'
5. VERDICT: "Move on" or "Review this topic"

Be strict. Do not give 2 unless genuinely correct."""
                    try:
                        eval_response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "You are a strict DSA interviewer. Evaluate honestly."},
                                {"role": "user", "content": eval_prompt}
                            ]
                        )
                        evaluation = eval_response.choices[0].message.content
                        st.markdown("### Evaluation")
                        st.markdown(evaluation)

                        # Robust regex score extraction
                        score_match = re.search(r'score\s*:\s*([012])', evaluation, re.IGNORECASE)
                        score = int(score_match.group(1)) if score_match else 1

                        st.session_state.db["gap_log"].append({
                            "type": "gap_entry",
                            "topic": st.session_state.get("current_topic", selected_topic),
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "score": score,
                            "evaluation": evaluation
                        })
                        save_data(st.session_state.db)
                        update_recommended_topic()

                        if score == 2:
                            st.session_state.brain["current_focus"] = None
                        else:
                            st.session_state.brain["current_focus"] = st.session_state.get("current_topic", selected_topic)

                        if score <= 1:
                            st.error(f"⚠️ {st.session_state.get('current_topic', selected_topic)} flagged as weak. Will resurface in 7 days.")
                        else:
                            st.success(f"✅ {st.session_state.get('current_topic', selected_topic)} marked solid.")
                    except Exception as e:
                        st.error(f"⚠️ Evaluation failed: {str(e)}")

# ==================== TAB 3 ====================
with tab3:
    st.session_state.brain["current_module"] = "FlowState"
    section_header("⚡", "FlowState", "Enter deep work mode with distraction-free coding sessions.", "#5C4B8A")
    st.caption("3PM–11PM | Check-in at 7PM | End of day at 11PM")

    today_str = datetime.now().strftime("%Y-%m-%d")
    weak = get_weak_topics(st.session_state.db.get("gap_log", []))
    weak_context = f"Weak topics due for retest: {', '.join(sorted(list({w['topic'] for w in weak if 'topic' in w})))}" if weak else "No weak topics flagged yet."

    st.markdown("### 📋 Daily Planning")
    priority1 = st.text_input("Priority 1 (most critical):", placeholder="e.g. Cold-solve sliding window")
    priority2 = st.text_input("Priority 2:", placeholder="e.g. Module 5 Day 51 notes")
    priority3 = st.text_input("Priority 3:", placeholder="e.g. NexusAI bug fixes")
    hours_available = st.slider("Hours available today:", 1, 8, 6)

    if st.button("Generate My Plan", key="gen_plan"):
        st.session_state.brain["last_activity"] = "Planning today's study session"
        if not priority1.strip():
            st.warning("Enter at least Priority 1.")
        else:
            with st.spinner("Building your day..."):
                plan_prompt = f"""You are a strict study planner.
Study window: 3PM to 11PM ({hours_available} hours available)
Check-in: 7PM | End of day: 11PM
Priorities:
1. {priority1}
2. {priority2 if priority2 else 'None'}
3. {priority3 if priority3 else 'None'}
Context: {weak_context}
Generate a specific hour-by-hour plan from 3PM to 11PM.
Include short breaks. Be realistic.
If weak topics exist, schedule retest time.
End with: MOST CRITICAL TASK TODAY: [one task]"""
                try:
                    plan_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict, realistic study planner. Specific time blocks only."},
                            {"role": "user", "content": plan_prompt}
                        ]
                    )
                    st.session_state.flow_plan = plan_response.choices[0].message.content
                except Exception as e:
                    st.error(f"⚠️ Could not generate plan: {str(e)}")

    if st.session_state.get("flow_plan"):
        st.markdown("### Your Plan")
        st.markdown(st.session_state.flow_plan)

        st.markdown("---")
        st.markdown("### ⏰ 7PM Check-in")
        checkin_report = st.text_area(
            "What actually happened since 3PM?",
            placeholder="e.g. Completed priority 1, got distracted for 1 hour",
            height=100,
            key="checkin"
        )

        if st.button("Replan 7PM-11PM", key="replan"):
            if len(checkin_report.strip()) < 10:
                st.warning("Report what actually happened before replanning.")
            else:
                with st.spinner("Replanning..."):
                    replan_prompt = f"""Original plan: {st.session_state.flow_plan}
What happened since 3PM: {checkin_report}
It is 7PM. 4 hours remain.
Generate revised plan for 7PM-11PM only.
Protect the most critical task above everything else."""
                    try:
                        replan_response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "You are a strict replanner. Protect critical tasks."},
                                {"role": "user", "content": replan_prompt}
                            ]
                        )
                        st.markdown("### Revised Plan (7PM-11PM)")
                        st.markdown(replan_response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"⚠️ Could not replan: {str(e)}")

        st.markdown("---")
        st.markdown("### 🌙 11PM End of Day")
        eod_report = st.text_area(
            "What did you complete today?",
            placeholder="e.g. Priority 1 done, Priority 2 half done",
            height=100,
            key="eod"
        )

        if st.button("Log Day", key="log_day"):
            if len(eod_report.strip()) < 10:
                st.warning("Report what you completed before logging.")
            else:
                with st.spinner("Logging your day..."):
                    eod_prompt = f"""Today's plan: {st.session_state.flow_plan}
What was completed: {eod_report}
Give:
1. COMPLETION RATE: % of planned work done
2. CARRY FORWARD: Uncompleted tasks for tomorrow
3. TOMORROW'S FOCUS: Single most important thing
4. HONEST ASSESSMENT: One sentence, no sugarcoating"""
                    try:
                        eod_response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "You are a strict daily reviewer. Honest assessment only."},
                                {"role": "user", "content": eod_prompt}
                            ]
                        )
                        review = eod_response.choices[0].message.content
                        st.markdown("### Day Review")
                        st.markdown(review)

                        st.session_state.db["day_logs"].append({
                            "date": today_str, "completed": eod_report, "review": review
                        })
                        save_data(st.session_state.db)
                        st.success("✅ Day logged. See you tomorrow.")
                    except Exception as e:
                        st.error(f"⚠️ Could not log day: {str(e)}")

# ==================== TAB 4 ====================
with tab4:
    st.session_state.brain["current_module"] = "Dashboard"
    section_header("📊", "Dashboard", "Track your progress and monitor long-term consistency.", "#2E6B52")
    st.caption("Your progress at a glance.")

    db = st.session_state.db
    gap_log = [e for e in db.get("gap_log", []) if isinstance(e, dict) and e.get("type") == "gap_entry"]
    day_logs = db.get("day_logs", [])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Problems Attempted", len(gap_log))
    with col2:
        st.metric("Marked Solid ✅", len([e for e in gap_log if e.get("score", 0) == 2]))
    with col3:
        st.metric("Flagged Weak ⚠️", len([e for e in gap_log if e.get("score", 0) <= 1]))
    with col4:
        st.metric("Days Logged", len(day_logs))

    st.markdown("---")
    st.markdown("### ⚠️ Weak Topics")
    weak_entries = [e for e in gap_log if e.get("score", 0) <= 1]

    if weak_entries:
        topic_data = {}
        for e in weak_entries:
            topic = e.get("topic", "General")
            if topic not in topic_data:
                topic_data[topic] = {"attempts": 0, "last_attempt": e.get("date", datetime.now().strftime("%Y-%m-%d"))}
            topic_data[topic]["attempts"] += 1
            if str(e.get("date", "")) > str(topic_data[topic]["last_attempt"]):
                topic_data[topic]["last_attempt"] = e.get("date", datetime.now().strftime("%Y-%m-%d"))

        for topic, data in topic_data.items():
            last_date = parse_date_safe(data["last_attempt"])
            days_since = (datetime.now().date() - last_date).days
            retest_due = "🔴 Due now" if days_since >= 7 else f"🟡 In {max(0, 7 - days_since)} days"
            st.markdown(f"**{topic}** — {data['attempts']} weak attempt(s) — Last: {data['last_attempt']} — Retest: {retest_due}")
    else:
        st.success("No weak topics yet. Keep solving.")

    st.markdown("---")
    st.markdown("### 📈 Topic Performance")
    if gap_log:
        topic_scores = {}
        for e in gap_log:
            topic = e.get("topic", "General")
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(e.get("score", 0))

        for topic, scores in topic_scores.items():
            if scores:
                avg = sum(scores) / len(scores)
                bar = "🟢" if avg >= 1.5 else "🟡" if avg >= 0.8 else "🔴"
                st.markdown(f"{bar} **{topic}** — {len(scores)} attempt(s) — Avg score: {avg:.1f}/2")
    else:
        st.info("No attempts logged yet. Start with GapFinder.")

    st.markdown("---")
    st.markdown("### 🌙 Recent Day Logs")
    if day_logs:
        for log in reversed(day_logs[-5:]):
            if isinstance(log, dict):
                with st.expander(f"📅 {log.get('date', 'Unknown Date')}"):
                    st.markdown(f"**Completed:** {log.get('completed', 'N/A')}")
                    st.markdown(f"**Review:** {log.get('review', 'N/A')}")
    else:
        st.info("No days logged yet. Use FlowState tonight.")

    st.markdown("---")
    if st.button("🔄 Refresh Dashboard", key="refresh"):
        st.session_state.db = load_data()
        st.rerun()

# ==================== TAB 5 ====================
with tab5:
    st.session_state.brain["current_module"] = "Mock Interview"
    section_header("🎤", "Mock Interview", "Practice technical interviews and receive AI-powered feedback.", "#7A3F3F")
    st.caption("Interview-format questions. Evaluated at the hiring bar.")

    db = st.session_state.db
    gap_log = [e for e in db.get("gap_log", []) if isinstance(e, dict) and e.get("type") == "gap_entry"]

    weak_topics_mock = sorted(list({e["topic"] for e in gap_log if e.get("score", 0) <= 1 and "topic" in e}))
    if weak_topics_mock:
        st.warning(f"⚠️ Recommended: Practice weak topics first — {', '.join(weak_topics_mock)}")

    topics = ["Prefix Sum", "Sliding Window", "Contribution Technique",
              "Bit Manipulation", "2D Matrices", "Strings"]

    col1, col2 = st.columns(2)
    with col1:
        interview_topic = st.selectbox("Select topic:", topics, key="mock_topic_select")
    with col2:
        difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard"], key="mock_diff_select")

    if st.button("Start Interview Question", key="start_interview"):
        st.session_state.brain["current_focus"] = interview_topic
        st.session_state.brain["last_activity"] = "Started a mock interview"
        with st.spinner("Preparing your interview question..."):
            question_prompt = f"""You are a technical interviewer at a product company hiring for an 18-22 LPA role.

Generate ONE interview question on: {interview_topic}
Difficulty: {difficulty}

Format exactly:
QUESTION: [problem statement, clear and complete]
WHAT WE'RE TESTING: [skill this evaluates]
TIME LIMIT: [realistic time in minutes]
WHAT A STRONG ANSWER LOOKS LIKE: [2-3 bullets — no solution, just what to cover]"""
            try:
                q_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"You are a strict technical interviewer for a {difficulty} {interview_topic} question."},
                        {"role": "user", "content": question_prompt}
                    ]
                )
                st.session_state.mock_question = q_response.choices[0].message.content
                st.session_state.mock_topic_val = interview_topic
                st.session_state.mock_difficulty_val = difficulty
            except Exception as e:
                st.error(f"⚠️ Could not start interview: {str(e)}")

    if "mock_question" in st.session_state and st.session_state.mock_question:
        st.markdown("### Your Question")
        st.markdown(st.session_state.mock_question)

        st.markdown("### ⏱️ Timer")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            if st.button("▶️ Start", key="start_timer"):
                st.session_state.timer_start = datetime.now()
                st.session_state.timer_running = True
                st.session_state.timer_result = None
        with col_t2:
            if st.button("⏹️ Stop", key="stop_timer"):
                if st.session_state.get("timer_running") and "timer_start" in st.session_state:
                    try:
                        elapsed = (datetime.now() - st.session_state.timer_start).total_seconds()
                        mins = int(elapsed // 60)
                        secs = int(elapsed % 60)
                        st.session_state.timer_result = f"{mins}m {secs}s"
                    except Exception:
                        st.session_state.timer_result = "Unknown time"
                    st.session_state.timer_running = False
        with col_t3:
            if st.button("🔄 Reset", key="reset_timer"):
                st.session_state.pop("timer_start", None)
                st.session_state.pop("timer_result", None)
                st.session_state.timer_running = False

        if st.session_state.get("timer_result"):
            try:
                mins_taken = int(st.session_state.timer_result.split("m")[0])
            except (ValueError, IndexError):
                mins_taken = 0
            st.info(f"⏱️ Time taken: {st.session_state.timer_result}")
            if mins_taken >= 20:
                st.warning("Over 20 minutes — flag this topic for extra practice.")

        st.markdown("### Your Answer")
        st.caption("Think out loud. Explain approach first, then solution — exactly like a real interview.")

        mock_answer = st.text_area(
            "Your answer:",
            height=250,
            placeholder="Explain your thought process first, then your approach, then your solution...",
            key="mock_answer"
        )

        if st.button("Evaluate My Answer", key="eval_mock"):
            if len(mock_answer.strip()) < 20:
                st.warning("Write a real answer before evaluating.")
            else:
                with st.spinner("Evaluating at the hiring bar..."):
                    eval_prompt = f"""You are a senior engineer interviewing for an 18-22 LPA role.

Question: {st.session_state.mock_question}
Candidate's answer: {mock_answer}
Topic: {st.session_state.get('mock_topic_val', 'General DSA')}
Difficulty: {st.session_state.get('mock_difficulty_val', 'Medium')}

Evaluate at the actual hiring bar:
1. COMMUNICATION: Did they explain thinking before jumping to code?
2. APPROACH: Correct and logical?
3. SOLUTION QUALITY: Correct, optimal, or flawed?
4. WHAT IMPRESSED: Specific positives
5. WHAT WOULD REJECT: Specific dealbreakers
6. HIRING VERDICT: "Strong Hire", "Hire", or "No Hire" — one sentence reason
7. WHAT TO SAY INSTEAD: Show exactly what a hired candidate would say for the weakest part"""
                    try:
                        eval_response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "You are a strict senior engineer interviewer. No sugarcoating. Weak answers get No Hire."},
                                {"role": "user", "content": eval_prompt}
                            ]
                        ]
                        evaluation = eval_response.choices[0].message.content
                        st.markdown("### Interviewer Evaluation")
                        st.markdown(evaluation)

                        verdict = "No Hire"
                        if "Strong Hire" in evaluation:
                            verdict = "Strong Hire"
                            st.success("✅ Strong Hire.")
                        elif "No Hire" in evaluation:
                            st.error("❌ No Hire — Review this topic.")
                        else:
                            verdict = "Hire"
                            st.warning("🟡 Hire — Room for improvement.")

                        st.session_state.db["gap_log"].append({
                            "type": "mock_entry",
                            "topic": st.session_state.get("mock_topic_val", "General"),
                            "difficulty": st.session_state.get("mock_difficulty_val", "Medium"),
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "verdict": verdict
                        })
                        save_data(st.session_state.db)
                    except Exception as e:
                        st.error(f"⚠️ Evaluation failed: {str(e)}")
