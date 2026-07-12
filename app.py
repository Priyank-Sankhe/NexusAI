import streamlit as st
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import threading
import copy

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

/* Sidebar Custom Button Styling to match selected state */
div[data-testid="stSidebar"] .stButton>button {
    background: rgba(59,42,30,.4);
    border: 1px solid rgba(255,255,255,.05);
    border-radius:12px;
    margin-bottom:8px;
    color: #D7C5B6;
}
div[data-testid="stSidebar"] .stButton>button:hover {
    background: #7D5436 !important;
    color: white !important;
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

.stAlert { border-radius:16px; border:none; box-shadow:0 8px 20px rgba(0,0,0,.18); }
</style>
""", unsafe_allow_html=True)

# ==================== CONFIG ====================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
BIN_ID = st.secrets["JSONBIN_BIN_ID"]
MASTER_KEY = st.secrets["JSONBIN_MASTER_KEY"]
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

MISSION_PENDING = "pending"
MISSION_ACTIVE = "active"
MISSION_COMPLETED = "completed"
MISSION_SKIPPED = "skipped"

# ==================== STORAGE ====================
def load_data():
    default_db = {
        "gap_log": [],
        "day_logs": [],
        "missions": [],
        "current_mission": None
    }
    try:
        response = requests.get(JSONBIN_URL, headers={"X-Master-Key": MASTER_KEY})
        data = response.json()["record"]
        for key, value in default_db.items():
            data.setdefault(key, value)
        return data
    except:
        return default_db

def _save_data_worker(data_snapshot):
    try:
        requests.put(
            JSONBIN_URL,
            headers={"X-Master-Key": MASTER_KEY, "Content-Type": "application/json"},
            json=data_snapshot
        )
    except:
        pass

def save_data(data):
    try:
        data_snapshot = copy.deepcopy(data)
        threading.Thread(target=_save_data_worker, args=(data_snapshot,), daemon=True).start()
    except:
        st.error("Failed to queue background data sync.")

# ==================== HELPERS ====================
def get_weak_topics(gap_log):
    weak = []
    today = datetime.now().date()
    for entry in gap_log:
        if entry.get("type") == "gap_entry":
            score = entry.get("score", 2)
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            days_since = (today - entry_date).days
            if score <= 1 and days_since >= 7:
                weak.append({"topic": entry["topic"], "days_since": days_since, "score": score})
    return weak

def create_mission(title, reason, priority, duration):
    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "title": title,
        "reason": reason,
        "priority": priority,
        "duration": duration,
        "status": MISSION_PENDING,
        "progress": 0,
        "started_at": None,
        "completed_at": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_daily_mission():
    weak_topics = get_weak_topics(st.session_state.db["gap_log"])
    if not weak_topics:
        return create_mission(
            title="Complete Today's Scaler Session",
            reason="No weak topics detected yet — keep solving problems.",
            priority=100,
            duration=60
        )
    weakest = sorted(weak_topics, key=lambda x: x["days_since"], reverse=True)[0]
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

# ==================== RUNTIME FRAGMENTS ====================
@st.fragment
def gap_timer_component():
    st.markdown("### ⏱️ Practice Timer")
    col_gt1, col_gt2, col_gt3 = st.columns(3)
    with col_gt1:
        if st.button("▶️ Start Timer", key="start_gap_timer"):
            st.session_state.gap_timer_start = datetime.now()
            st.session_state.gap_timer_running = True
            st.session_state.gap_timer_result = None
    with col_gt2:
        if st.button("⏹️ Stop Timer", key="stop_gap_timer"):
            if st.session_state.get("gap_timer_running") and "gap_timer_start" in st.session_state:
                elapsed = (datetime.now() - st.session_state.gap_timer_start).seconds
                mins = elapsed // 60
                secs = elapsed % 60
                st.session_state.gap_timer_result = f"{mins}m {secs}s"
                st.session_state.gap_timer_running = False
    with col_gt3:
        if st.button("🔄 Reset Timer", key="reset_gap_timer"):
            st.session_state.pop("gap_timer_start", None)
            st.session_state.pop("gap_timer_result", None)
            st.session_state.gap_timer_running = False

    if st.session_state.get("gap_timer_result"):
        st.info(f"⏱️ Time taken to solve: {st.session_state.gap_timer_result}")

@st.fragment
def mock_timer_component():
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
                elapsed = (datetime.now() - st.session_state.timer_start).seconds
                mins = elapsed // 60
                secs = elapsed % 60
                st.session_state.timer_result = f"{mins}m {secs}s"
                st.session_state.timer_running = False
    with col_t3:
        if st.button("🔄 Reset", key="reset_timer"):
            st.session_state.pop("timer_start", None)
            st.session_state.pop("timer_result", None)
            st.session_state.timer_running = False

    if st.session_state.get("timer_result"):
        mins_taken = int(st.session_state.timer_result.split("m")[0])
        st.info(f"⏱️ Time taken: {st.session_state.timer_result}")
        if mins_taken >= 20:
            st.warning("Over 20 minutes — flag this topic for extra practice.")

# ==================== SESSION STATE ====================
if "db" not in st.session_state:
    st.session_state.db = load_data()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "flow_plan" not in st.session_state:
    st.session_state.flow_plan = None
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "gap_timer_running" not in st.session_state:
    st.session_state.gap_timer_running = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "📊 Dashboard"
if "brain" not in st.session_state:
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

# ==================== MISSION ENGINE ====================
def update_recommended_topic():
    weak_topics = get_weak_topics(st.session_state.db["gap_log"])
    if weak_topics:
        weakest = sorted(weak_topics, key=lambda x: x["days_since"], reverse=True)[0]
        st.session_state.brain["recommended_topic"] = weakest["topic"]
    else:
        st.session_state.brain["recommended_topic"] = None

update_recommended_topic()

if st.session_state.db["current_mission"] is None:
    mission = generate_daily_mission()
    if mission:
        st.session_state.db["missions"].append(mission)
        st.session_state.db["current_mission"] = mission
        st.session_state.brain["current_focus"] = mission["title"]
        st.session_state.brain["recommended_action"] = "Start Mission"
        save_data(st.session_state.db)

mission = st.session_state.db.get("current_mission")
if mission:
    mission.setdefault("progress", 0)
    mission.setdefault("duration", 25)
    mission.setdefault("status", MISSION_PENDING)
    mission.setdefault("reason", "")
    mission.setdefault("started_at", None)
    mission.setdefault("completed_at", None)

# ==================== NAVIGATION CALLBACKS ====================
def set_page(page_name):
    st.session_state.current_page = page_name

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🧠 NexusAI")
    st.caption("AI Software Engineering Coach")
    st.divider()

    gap_log_s = st.session_state.db["gap_log"]
    day_logs_s = st.session_state.db["day_logs"]

    st.metric("📚 Problems", len([e for e in gap_log_s if e.get("type") == "gap_entry"]))
    st.metric("🎯 Weak Topics", len({e["topic"] for e in gap_log_s if e.get("type") == "gap_entry" and e.get("score", 0) <= 1}))
    st.metric("📅 Study Days", len(day_logs_s))

    st.divider()
    st.markdown("### 🚀 Today's Goal")
    st.progress(0.60)
    st.caption("Complete today's Scaler session")
    st.divider()

    st.markdown("### ⚡ Quick Actions")
    # State-driven router mapping
    pages = ["📊 Dashboard", "💬 Study Chat", "🎯 GapFinder", "⚡ FlowState", "🎤 Mock Interview"]
    for p in pages:
        # Highlight active view using simple visual cues
        label = f"• {p} •" if st.session_state.current_page == p else p
        if st.button(label, key=f"nav_{p}", use_container_width=True):
            set_page(p)
            st.rerun()
            
    st.divider()
    st.caption("NexusAI v1.0")

# ==================== RENDER COMPONENT CONTROLLERS ====================

if st.session_state.current_page == "📊 Dashboard":
    st.session_state.brain["current_module"] = "Dashboard"
    
    # Hero Summary
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    hour = now.hour
    today_name = now.strftime("%A")

    if hour < 12: greeting = "Good Morning ☀️"
    elif hour < 17: greeting = "Good Afternoon 🌤️"
    else: greeting = "Good Evening 🌙"

    gap_log_h = st.session_state.db["gap_log"]
    day_logs_h = st.session_state.db["day_logs"]
    problem_count = len([e for e in gap_log_h if e.get("type") == "gap_entry"])
    weak_count = len({e["topic"] for e in gap_log_h if e.get("type") == "gap_entry" and e.get("score", 0) <= 1})
    day_count = len(day_logs_h)

    hero = st.container(border=True)
    with hero:
        left, right = st.columns([4, 1])
        with left:
            st.title("🧠 Command Center")
            st.subheader(greeting)
            st.write("### Ready to continue your Software Engineering journey?")
            st.caption("Every coding session brings you closer to becoming a Software Engineer.")
        with right:
            st.markdown(f"### 📅 {today_name}")

    st.write("")
    a, b, c = st.columns(3)
    with a: st.metric("📚 Problems Solved", problem_count)
    with b: st.metric("🎯 Weak Topics", weak_count)
    with c: st.metric("📅 Study Days", day_count)
    st.write("")

    # AI Recommendation
    brain = st.session_state.brain
    recommended_topic = brain.get("recommended_topic")

    if recommended_topic:
        recommendation = f"🧠 **NexusAI Recommendation:** Your highest priority right now is **{recommended_topic}**. Strengthen this topic before moving on."
    elif brain["current_focus"]:
        recommendation = f"🎯 **Status:** Continue working on active focus: **{brain['current_focus']}**."
    elif mission and mission["status"] == MISSION_PENDING:
        recommendation = f"🚀 **Status:** Start today's queued mission: **{mission['title']}**."
    else:
        recommendation = "💡 **Status:** Clear skies! Generate a new GapFinder problem to keep improving."

    st.info(recommendation)

    if recommended_topic:
        if st.button(f"🎯 Route to GapFinder to Practice {recommended_topic}", use_container_width=True):
            st.session_state.brain["current_focus"] = recommended_topic
            set_page("🎯 GapFinder")
            st.rerun()
    elif mission and mission["status"] == MISSION_PENDING:
        if st.button("🚀 Start Current Mission", use_container_width=True):
            mission["status"] = MISSION_ACTIVE
            mission["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(st.session_state.db)
            st.rerun()

    # Current Mission Card
    st.markdown("---")
    st.markdown("### 🎯 Active Mission Track")
    mission_card = st.container(border=True)
    with mission_card:
        if mission:
            left, right = st.columns([3, 1])
            with left:
                st.subheader(mission["title"])
                priority = mission.get("priority", 100)
                if priority >= 90: st.success("🔥 High Priority")
                elif priority >= 60: st.warning("⚡ Medium Priority")
                else: st.info("📌 Low Priority")

                st.caption(mission["reason"])

                if mission["status"] == MISSION_ACTIVE and mission["started_at"]:
                    started = datetime.strptime(mission["started_at"], "%Y-%m-%d %H:%M:%S")
                    elapsed_seconds = (datetime.now() - started).total_seconds()
                    total_seconds = mission["duration"] * 60
                    progress = min(100, int((elapsed_seconds / total_seconds) * 100))
                    mission["progress"] = progress

                st.progress(mission["progress"] / 100)
                st.caption(f"Progress: {mission['progress']}%")

            with right:
                st.metric("Duration", f"{mission['duration']} min")
                st.metric("Status", mission["status"].title())

                if mission["status"] == MISSION_PENDING:
                    if st.button("▶ Start Mission", key="dash_start_mission", use_container_width=True):
                        mission["status"] = MISSION_ACTIVE
                        mission["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_data(st.session_state.db)
                        st.rerun()

                if mission["status"] == MISSION_ACTIVE:
                    if st.button("✅ Complete Mission", key="dash_complete_mission", use_container_width=True):
                        mission["status"] = MISSION_COMPLETED
                        mission["progress"] = 100
                        mission["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.db["current_mission"] = None
                        save_data(st.session_state.db)
                        st.rerun()
        else:
            st.info("No active mission yet. Solve problems in GapFinder to generate performance markers.")

    # Analytical Logs (Moved inside Dashboard view where they belong)
    st.markdown("---")
    st.markdown("### ⚠️ Tracked Gaps & Retest Windows")
    db = st.session_state.db
    gap_log = [e for e in db["gap_log"] if e.get("type") == "gap_entry"]
    day_logs = db["day_logs"]
    weak_entries = [e for e in gap_log if e.get("score", 0) <= 1]

    if weak_entries:
        topic_data = {}
        for e in weak_entries:
            topic = e["topic"]
            if topic not in topic_data:
                topic_data[topic] = {"attempts": 0, "last_attempt": e["date"]}
            topic_data[topic]["attempts"] += 1
            if e["date"] > topic_data[topic]["last_attempt"]:
                topic_data[topic]["last_attempt"] = e["date"]

        for topic, data in topic_data.items():
            days_since = (datetime.now().date() - datetime.strptime(data["last_attempt"], "%Y-%m-%d").date()).days
            retest_due = "🔴 Due now" if days_since >= 7 else f"🟡 In {7 - days_since} days"
            st.markdown(f"**{topic}** — {data['attempts']} weak attempt(s) — Last: {data['last_attempt']} — Retest: {retest_due}")
    else:
        st.success("No weak metrics flagged yet.")

    st.markdown("---")
    st.markdown("### 📈 Analytics Matrix")
    if gap_log:
        topic_scores = {}
        for e in gap_log:
            topic = e["topic"]
            if topic not in topic_scores: topic_scores[topic] = []
            topic_scores[topic].append(e.get("score", 0))

        for topic, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            bar = "🟢" if avg >= 1.5 else "🟡" if avg >= 0.8 else "🔴"
            st.markdown(f"{bar} **{topic}** — {len(scores)} attempt(s) — Avg score: {avg:.1f}/2")
    else:
        st.info("No metrics tracked yet. Practice code concepts via side modules to populate charts.")

    st.markdown("---")
    st.markdown("### 🌙 Archived Day Logs")
    if day_logs:
        for log in reversed(day_logs[-5:]):
            with st.expander(f"📅 {log['date']}"):
                st.markdown(f"**Completed:** {log['completed']}")
                st.markdown(f"**Review:** {log['review']}")
    else:
        st.info("No study intervals closed yet.")

elif st.session_state.current_page == "💬 Study Chat":
    st.session_state.brain["current_module"] = "Study Chat"
    section_header("💬", "Study Chat", "Ask anything about your Scaler journey. NexusAI remembers your learning context.", "#385C7A")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask anything...")

    if user_input:
        st.session_state.brain["last_activity"] = "Asked a study question"
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        brain = st.session_state.brain
        brain_context = f"CURRENT AI STATE\nCurrent Focus: {brain.get('current_focus')}\nRecommended Topic: {brain.get('recommended_topic')}\nCurrent Module: {brain.get('current_module')}\nLast Activity: {brain.get('last_activity')}\n"
        system_context = brain_context + """You are NexusAI, a specialized software engineering study assistant.
STUDENT PROFILE:
- Name: Shivang
- Program: Scaler Academy Software Development Program
- Current module: Module 5 (AI & Agents)
- Completed: Java basics, intermediate DSA (arrays, prefix sum, carry forward, contribution technique, sliding window, bit manipulation, 2D matrices, strings)
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
SCOPE: Only answer questions about software engineering, DSA, Java, Python, system design, Scaler curriculum, career strategy, and AI/ML from Module 5. Redirect anything outside this scope."""

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
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

elif st.session_state.current_page == "🎯 GapFinder":
    st.session_state.brain["current_module"] = "GapFinder"
    section_header("🎯", "GapFinder", "Identify weak concepts and automatically generate targeted practice.", "#7A5636")

    weak_topics = get_weak_topics(st.session_state.db["gap_log"])
    if weak_topics:
        st.warning(f"⚠️ Topics due for retest: {', '.join(set([w['topic'] for w in weak_topics]))}")

    topics = ["Prefix Sum", "Sliding Window", "Contribution Technique", "Bit Manipulation", "2D Matrices", "Strings"]
    recommended = st.session_state.brain.get("recommended_topic")
    default_index = 0
    if recommended in topics: default_index = topics.index(recommended)

    selected_topic = st.selectbox("Select a topic:", topics, index=default_index, key="gap_topic")

    if st.button("Generate Problem", key="gen_problem"):
        st.session_state.brain["current_focus"] = selected_topic
        st.session_state.brain["last_activity"] = "Generated a practice problem"
        with st.spinner("Generating problem..."):
            problem_prompt = f"Generate a DSA problem specifically and only on: {selected_topic}.\nFormat exactly like this:\nPROBLEM: [clear problem statement with example input and output]\nDIFFICULTY: [Easy/Medium]\nHINT: [one line hint, not the solution]"
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are a DSA problem generator. Only generate problems about {selected_topic}."},
                    {"role": "user", "content": problem_prompt}
                ]
            )
            st.session_state.current_problem = response.choices[0].message.content
            st.session_state.current_topic = selected_topic

    if "current_problem" in st.session_state:
        st.markdown("### Problem")
        st.markdown(st.session_state.current_problem)

        gap_timer_component()

        user_solution = st.text_area("Write your approach — pseudocode, logic, or actual code:", height=200, key="solution_input")

        if st.button("Evaluate My Solution", key="eval_solution"):
            if len(user_solution.strip()) < 10:
                st.warning("Write an actual solution attempt before evaluating.")
            else:
                with st.spinner("Evaluating..."):
                    eval_prompt = f"Problem: {st.session_state.current_problem}\n\nStudent's solution: {user_solution}\n\nEvaluate strictly:\n1. CORRECT: What did they get right?\n2. MISSING: What's wrong or missing?\n3. OPTIMAL SOLUTION: Show the correct approach\n4. SCORE: 0 (wrong), 1 (partial), 2 (correct) — number only\n5. VERDICT: \"Move on\" or \"Review this topic\"\n\nBe strict. Do not give 2 unless genuinely correct."
                    eval_response = client.chat.completions.create(
                        model="llama-3.3-70b-specdec",
                        messages=[
                            {"role": "system", "content": "You are a strict DSA interviewer. Evaluate honestly."},
                            {"role": "user", "content": eval_prompt}
                        ]
                    )
                    evaluation = eval_response.choices[0].message.content
                    st.markdown("### Evaluation")
                    st.markdown(evaluation)

                    score = 1
                    for line in evaluation.split("\n"):
                        if "SCORE:" in line:
                            if "0" in line: score = 0
                            elif "2" in line: score = 2
                            break

                    st.session_state.db["gap_log"].append({
                        "type": "gap_entry",
                        "topic": st.session_state.current_topic,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "score": score,
                        "evaluation": evaluation
                    })
                    save_data(st.session_state.db)
                    update_recommended_topic()

                    if score == 2: st.session_state.brain["current_focus"] = None
                    else: st.session_state.brain["current_focus"] = st.session_state.current_topic

                    if score <= 1: st.error(f"⚠️ {st.session_state.current_topic} flagged as weak. Will resurface in 7 days.")
                    else: st.success(f"✅ {st.session_state.current_topic} marked solid.")

elif st.session_state.current_page == "⚡ FlowState":

    st.session_state.brain["current_module"] = "FlowState"

    section_header(
        "⚡",
        "FlowState",
        "Deep work. Zero distractions. Maximum consistency.",
        "#5C4B8A"
    )

    brain = st.session_state.brain
    mission = st.session_state.db.get("current_mission")

    st.markdown("## 🎯 Mission Control")

    mission_card = st.container(border=True)

    with mission_card:

        if mission:

            left,right = st.columns([3,1])

            with left:

                st.subheader(mission["title"])

                st.caption(mission["reason"])

                st.progress(mission["progress"]/100)

            with right:

                st.metric(
                    "Progress",
                    f"{mission['progress']}%"
                )

                st.metric(
                    "Status",
                    mission["status"].title()
                )

        else:

            st.info(
                "No mission available."
            )

    st.write("")

    st.markdown("## 🧠 AI Focus")

    c1,c2 = st.columns(2)

    with c1:

        st.info(
            f"Current Focus\n\n"
            f"**{brain.get('current_focus') or 'None'}**"
        )

    with c2:

        st.info(
            f"Recommended Topic\n\n"
            f"**{brain.get('recommended_topic') or 'None'}**"
        )

    st.write("")

    st.markdown("## 🎯 Focus Session")

    focus_card = st.container(border=True)

    with focus_card:

        duration = st.selectbox(

            "Focus Duration",

            [

                25,

                50,

                90

            ],

            key="focus_duration"

        )

        col1,col2,col3 = st.columns(3)

        with col1:

            if st.button(

                "▶ Start Focus",

                use_container_width=True,

                key="focus_start_btn"

            ):

                st.session_state.focus_running = True

                st.session_state.focus_start = datetime.now()

                brain["last_activity"] = "Started Focus Session"

                save_data(st.session_state.db)

                st.success("Focus session started.")

        with col2:

            if st.button(

                "⏸ Pause",

                use_container_width=True,

                key="focus_pause_btn"

            ):

                st.session_state.focus_running = False

                brain["last_activity"] = "Paused Focus Session"

                st.warning("Focus paused.")

        with col3:

            if st.button(

                "✅ Complete",

                use_container_width=True,

                key="focus_complete_btn"

            ):

                if st.session_state.get("focus_start"):

                    elapsed = int(

                        (

                            datetime.now()

                            -

                            st.session_state.focus_start

                        ).total_seconds()

                        /

                        60

                    )

                else:

                    elapsed = 0

                st.success(

                    f"Completed {elapsed} minute(s)."

                )

                brain["last_activity"] = "Completed Focus Session"

                brain["current_focus"] = None

                if mission:

                    mission["progress"] = min(

                        100,

                        mission["progress"] + 20

                    )

                    if mission["progress"] >= 100:

                        mission["status"] = MISSION_COMPLETED

                        mission["completed_at"] = datetime.now().strftime(

                            "%Y-%m-%d %H:%M:%S"

                        )

                save_data(st.session_state.db)

                st.session_state.focus_running = False

    st.write("")

    st.markdown("## 📋 AI Daily Planner")
        today = datetime.now().strftime("%Y-%m-%d")

    weak_topics = get_weak_topics(
        st.session_state.db["gap_log"]
    )

    weak_context = (
        ", ".join(
            sorted(
                list(
                    set(
                        w["topic"] for w in weak_topics
                    )
                )
            )
        )
        if weak_topics
        else "None"
    )

    st.markdown("### Today's Priorities")

    priority1 = st.text_input(
        "Priority 1",
        placeholder="Most important task",
        key="flow_priority1"
    )

    priority2 = st.text_input(
        "Priority 2",
        placeholder="Second priority",
        key="flow_priority2"
    )

    priority3 = st.text_input(
        "Priority 3",
        placeholder="Third priority",
        key="flow_priority3"
    )

    hours_available = st.slider(
        "Hours Available Today",
        1,
        10,
        6,
        key="flow_hours"
    )

    if st.button(
        "🧠 Generate AI Plan",
        use_container_width=True,
        key="generate_flow_plan"
    ):

        if priority1.strip() == "":

            st.warning(
                "Priority 1 is required."
            )

        else:

            brain["last_activity"] = "Generated Daily Plan"

            mission_text = (
                mission["title"]
                if mission
                else "None"
            )

            recommended = (
                brain.get("recommended_topic")
                or "None"
            )

            current_focus = (
                brain.get("current_focus")
                or "None"
            )

            yesterday = ""

            if st.session_state.db["day_logs"]:

                yesterday = st.session_state.db["day_logs"][-1]["review"]

            else:

                yesterday = "No previous review."

            planner_prompt = f"""
You are NexusAI.

Generate today's study plan.

MISSION:
{mission_text}

CURRENT FOCUS:
{current_focus}

RECOMMENDED TOPIC:
{recommended}

WEAK TOPICS:
{weak_context}

AVAILABLE HOURS:
{hours_available}

USER PRIORITIES:

1.
{priority1}

2.
{priority2 or "None"}

3.
{priority3 or "None"}

YESTERDAY'S REVIEW:
{yesterday}

Requirements:

- Produce an hour-by-hour study schedule.

- Include focused work blocks.

- Include breaks.

- Include revision if weak topics exist.

- Prioritize today's mission.

- Finish with:

MOST IMPORTANT TASK TODAY:
"""

            with st.spinner(
                "Generating your study plan..."
            ):

                response = client.chat.completions.create(

                    model="llama-3.1-8b-instant",

                    messages=[

                        {
                            "role":"system",
                            "content":"You are an elite study planner."
                        },

                        {
                            "role":"user",
                            "content":planner_prompt
                        }

                    ]

                )

            st.session_state.flow_plan = (
                response
                .choices[0]
                .message
                .content
            )

    if st.session_state.flow_plan:

        st.markdown("### 📅 Today's Plan")

        plan_card = st.container(border=True)

        with plan_card:

            st.markdown(
                st.session_state.flow_plan
            )

        st.success(
            "Plan ready. Begin your first focus session."
        )

    st.write("")
    # ==========================================================
    # AI CHECK-IN
    # ==========================================================

    st.markdown("## 🌇 Mid-Day Check-in")

    checkin_card = st.container(border=True)

    with checkin_card:

        st.caption(
            "Reflect honestly before NexusAI replans the rest of your day."
        )

        checkin_report = st.text_area(

            "What happened since your first study session?",

            placeholder="Example: Finished Priority 1, got stuck on Sliding Window for 45 minutes.",

            height=150,

            key="flow_checkin"

        )

        if st.button(

            "🔄 Replan Remaining Day",

            use_container_width=True,

            key="flow_replan_btn"

        ):

            if len(checkin_report.strip()) < 10:

                st.warning(
                    "Describe your progress before requesting a new plan."
                )

            else:

                brain["last_activity"] = "Requested Mid-Day Replan"

                mission_text = (
                    mission["title"]
                    if mission
                    else "None"
                )

                focus = (
                    brain.get("current_focus")
                    or "None"
                )

                recommended = (
                    brain.get("recommended_topic")
                    or "None"
                )

                replan_prompt = f"""
You are NexusAI.

The student already followed part of today's study plan.

ORIGINAL PLAN

{st.session_state.flow_plan}

MISSION

{mission_text}

CURRENT FOCUS

{focus}

RECOMMENDED TOPIC

{recommended}

CHECK-IN REPORT

{checkin_report}

Generate ONLY the remaining schedule.

Requirements:

• Protect today's mission.

• Continue unfinished priorities.

• If the student is behind,
compress lower-priority work.

• If the student is ahead,
increase revision.

• Include realistic breaks.

Finish with:

NEXT MOST IMPORTANT ACTION:
"""

                with st.spinner(
                    "Replanning..."
                ):

                    response = client.chat.completions.create(

                        model="llama-3.1-8b-instant",

                        messages=[

                            {
                                "role":"system",
                                "content":"You are an expert productivity coach."
                            },

                            {
                                "role":"user",
                                "content":replan_prompt
                            }

                        ]

                    )

                replanned_schedule = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                st.markdown("### 🔁 Revised Schedule")

                replanner_card = st.container(border=True)

                with replanner_card:

                    st.markdown(
                        replanned_schedule
                    )

                brain["last_activity"] = "Received Revised Plan"

                st.success(
                    "Remaining schedule optimized."
                )

    st.write("")
    # ==========================================================
    # END OF DAY REVIEW
    # ==========================================================

    st.markdown("## 🌙 End of Day Review")

    review_card = st.container(border=True)

    with review_card:

        completed_work = st.text_area(

            "What did you complete today?",

            placeholder="Example: Finished Prefix Sum revision, solved 3 Sliding Window problems, completed today's Scaler lecture.",

            height=150,

            key="flow_completed_today"

        )

        if st.button(

            "📝 Generate Daily Review",

            use_container_width=True,

            key="flow_generate_review"

        ):

            if len(completed_work.strip()) < 10:

                st.warning(
                    "Describe today's work before generating a review."
                )

            else:

                brain["last_activity"] = "Generated End-of-Day Review"

                mission_text = (
                    mission["title"]
                    if mission
                    else "None"
                )

                review_prompt = f"""
You are NexusAI.

Today's Mission

{mission_text}

Today's Plan

{st.session_state.flow_plan}

Completed Work

{completed_work}

Generate:

## Completion Rate

## Wins

## Missed Work

## Carry Forward

## Tomorrow's Highest Priority

## Honest Assessment

Keep the feedback constructive but realistic.
"""

                with st.spinner(
                    "Reviewing your day..."
                ):

                    response = client.chat.completions.create(

                        model="llama-3.1-8b-instant",

                        messages=[

                            {
                                "role":"system",
                                "content":"You are a strict productivity coach."
                            },

                            {
                                "role":"user",
                                "content":review_prompt
                            }

                        ]

                    )

                daily_review = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                st.markdown("### 📋 Daily Review")

                review_output = st.container(border=True)

                with review_output:

                    st.markdown(
                        daily_review
                    )

                st.session_state.db["day_logs"].append({

                    "date": today,

                    "completed": completed_work,

                    "review": daily_review

                })

                save_data(
                    st.session_state.db
                )

                st.success(
                    "Day successfully logged."
                )

    st.write("")

    # ==========================================================
    # TODAY'S PRODUCTIVITY
    # ==========================================================

    st.markdown("## 📊 Today's Productivity")

    analytics = st.container(border=True)

    with analytics:

        total_focus = 0

        if st.session_state.get("focus_start"):

            if st.session_state.get("focus_running"):

                total_focus = int(

                    (

                        datetime.now()

                        -

                        st.session_state.focus_start

                    ).total_seconds()

                    /

                    60

                )

        mission_progress = 0

        if mission:

            mission_progress = mission.get(
                "progress",
                0
            )

        col1,col2,col3 = st.columns(3)

        with col1:

            st.metric(

                "Focus Minutes",

                total_focus

            )

        with col2:

            st.metric(

                "Mission Progress",

                f"{mission_progress}%"

            )

        with col3:

            st.metric(

                "Study Days",

                len(
                    st.session_state.db["day_logs"]
                )

            )

    st.write("")
    # ==========================================================
    # AI BRAIN SYNCHRONIZATION
    # ==========================================================

    brain = st.session_state.brain

    if mission:

        if mission["status"] == MISSION_ACTIVE:

            brain["current_focus"] = mission["title"]

        elif mission["status"] == MISSION_COMPLETED":

            brain["current_focus"] = None

    update_recommended_topic()

    # ==========================================================
    # MISSION STATUS
    # ==========================================================

    if mission:

        if mission["status"] == MISSION_COMPLETED:

            st.success("🏆 Mission Completed")

            st.balloons()

            if st.button(
                "🎯 Generate Next Mission",
                use_container_width=True,
                key="generate_next_mission_btn"
            ):

                new_mission = generate_daily_mission()

                if new_mission:

                    st.session_state.db["missions"].append(
                        new_mission
                    )

                    st.session_state.db["current_mission"] = (
                        new_mission
                    )

                    save_data(
                        st.session_state.db
                    )

                    st.success(
                        "New mission generated."
                    )

                    st.rerun()

    # ==========================================================
    # AUTO SAVE
    # ==========================================================

    save_data(
        st.session_state.db
    )

    # ==========================================================
    # FLOWSTATE FOOTER
    # ==========================================================

    st.divider()

    st.caption(
        "FlowState synchronizes your mission, AI Brain, study plans and daily progress automatically."
    )

elif st.session_state.current_page == "🎤 Mock Interview":
    st.session_state.brain["current_module"] = "Mock Interview"
    section_header("🎤", "Mock Interview", "Practice technical interviews and receive AI-powered feedback.", "#7A3F3F")

    db = st.session_state.db
    gap_log = [e for e in db["gap_log"] if e.get("type") == "gap_entry"]

    weak_topics_mock = list(set([e["topic"] for e in gap_log if e.get("score", 0) <= 1]))
    if weak_topics_mock:
        st.warning(f"⚠️ Recommended: Practice weak topics first — {', '.join(weak_topics_mock)}")

    topics = ["Prefix Sum", "Sliding Window", "Contribution Technique", "Bit Manipulation", "2D Matrices", "Strings"]

    col1, col2 = st.columns(2)
    with col1: interview_topic = st.selectbox("Select topic:", topics, key="mock_topic_select")
    with col2: difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard"], key="mock_diff_select")

    if st.button("Start Interview Question", key="start_interview"):
        st.session_state.brain["current_focus"] = interview_topic
        st.session_state.brain["last_activity"] = "Started a mock interview"
        with st.spinner("Preparing your interview question..."):
            question_prompt = f"You are a technical interviewer at a product company hiring for an 18-22 LPA role.\n\nGenerate ONE interview question on: {interview_topic}\nDifficulty: {difficulty}\n\nFormat exactly:\nQUESTION: [problem statement, clear and complete]\nWHAT WE'RE TESTING: [skill this evaluates]\nTIME LIMIT: [realistic time in minutes]\nWHAT A STRONG ANSWER LOOKS LIKE: [2-3 bullets — no solution, just what to cover]"
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

    if "mock_question" in st.session_state:
        st.markdown("### Your Question")
        st.markdown(st.session_state.mock_question)

        mock_timer_component()

        st.markdown("### Your Answer")
        mock_answer = st.text_area("Your answer:", height=250, placeholder="Explain your thought process first, then your approach, then your solution...", key="mock_answer")

        if st.button("Evaluate My Answer", key="eval_mock"):
            if len(mock_answer.strip()) < 20: st.warning("Write a real answer before evaluating.")
            else:
                with st.spinner("Evaluating at the hiring bar..."):
                    eval_prompt = f"You are a senior engineer interviewing for an 18-22 LPA role.\n\nQuestion: {st.session_state.mock_question}\nCandidate's answer: {mock_answer}\nTopic: {st.session_state.mock_topic_val}\nDifficulty: {st.session_state.mock_difficulty_val}\n\nEvaluate at the actual hiring bar:\n1. COMMUNICATION: Did they explain thinking before jumping to code?\n2. APPROACH: Correct and logical?\n3. SOLUTION QUALITY: Correct, optimal, or flawed?\n4. WHAT IMPRESSED: Specific positives\n5. WHAT WOULD REJECT: Specific dealbreakers\n6. HIRING VERDICT: \"Strong Hire\", \"Hire\", or \"No Hire\" — one sentence reason\n7. WHAT TO SAY INSTEAD: Show exactly what a hired candidate would say for the weakest part"
                    eval_response = client.chat.completions.create(
                        model="llama-3.3-70b-specdec",
                        messages=[
                            {"role": "system", "content": "You are a strict senior engineer interviewer. No sugarcoating. Weak answers get No Hire."},
                            {"role": "user", "content": eval_prompt}
                        ]
                    )
                    evaluation = eval_response.choices[0].message.content
                    st.markdown("### Interviewer Evaluation")
                    st.markdown(evaluation)

                    verdict = "No Hire"
                    if "Strong Hire" in evaluation:
                        verdict = "Strong Hire"; st.success("✅ Strong Hire.")
                    elif "No Hire" in evaluation:
                        st.error("❌ No Hire — Review this topic.")
                    else:
                        verdict = "Hire"; st.warning("🟡 Hire — Room for improvement.")

                    st.session_state.db["gap_log"].append({
                        "type": "mock_entry",
                        "topic": st.session_state.mock_topic_val,
                        "difficulty": st.session_state.mock_difficulty_val,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "verdict": verdict
                    })
                    save_data(st.session_state.db)
