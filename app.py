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
header {
    background: transparent !important;
}

.stApp {
    background-color: #0F172A;
    background-image: 
        radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.12), transparent 40%),
        radial-gradient(circle at 85% 100%, rgba(14, 165, 233, 0.08), transparent 40%);
    color: #CBD5E1;
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: radial-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events: none;
    z-index: -1;
}

.block-container {
    max-width: 1200px;
    padding-top: 3rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

h1, h2, h3, h4 {
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}
h1 { color: #F8FAFC; font-weight: 700; }
h2 { color: #F8FAFC; font-weight: 600; }
h3 { color: #CBD5E1; font-weight: 600; }
h4 { color: #94A3B8; font-weight: 500; }

[data-testid="metric-container"] {
    background: rgba(26, 36, 56, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.15);
    background: rgba(26, 36, 56, 0.6);
}

.stButton>button {
    width: 100%;
    border: 1px solid rgba(56, 189, 248, 0.8);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-weight: 500;
    font-size: 0.9rem;
    color: #F8FAFC;
    background: linear-gradient(180deg, #38BDF8 0%, #0EA5E9 100%);
    box-shadow: 0 1px 2px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.2);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.stButton>button:hover {
    border-color: #0EA5E9;
    background: linear-gradient(180deg, #0EA5E9 0%, #0284C7 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.25), inset 0 1px 0 rgba(255,255,255,0.25);
}
.stButton>button:active {
    transform: translateY(0);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
}

div[data-testid="stSidebar"] .stButton>button {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    margin-bottom: 4px;
    color: #94A3B8;
    box-shadow: none;
    justify-content: flex-start;
    font-weight: 500;
    padding: 0.5rem 0.75rem;
    transition: all 0.15s ease;
}
div[data-testid="stSidebar"] .stButton>button:hover {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.04);
    color: #F8FAFC !important;
    transform: none;
    box-shadow: none;
}

.stTextInput input, .stTextArea textarea {
    background: rgba(17, 24, 39, 0.6) !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    transition: all 0.2s ease !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.2) !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(56, 189, 248, 0.6) !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15) !important;
    background: rgba(17, 24, 39, 0.9) !important;
}

.stSelectbox div[data-baseweb="select"] {
    background: rgba(17, 24, 39, 0.6);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: all 0.2s ease;
}
.stSelectbox div[data-baseweb="select"]:focus-within {
    border-color: rgba(56, 189, 248, 0.6);
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15);
    background: rgba(17, 24, 39, 0.9);
}

.stSlider { 
    padding-top: 1rem; 
}

[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.3);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 1.25rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stSuccess, .stWarning, .stError, .stInfo, .stAlert { 
    border-radius: 10px; 
    border: 1px solid rgba(255, 255, 255, 0.06); 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); 
    background: rgba(26, 36, 56, 0.85); 
    backdrop-filter: blur(12px); 
}

.streamlit-expanderHeader { 
    background: transparent !important; 
    border-radius: 8px; 
    font-weight: 500; 
    transition: background 0.2s ease; 
}
.streamlit-expanderHeader:hover { 
    background: rgba(255, 255, 255, 0.03) !important; 
}

hr { 
    border: none; 
    height: 1px; 
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent); 
    margin: 2.5rem 0;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56, 189, 248, 0.2); border-radius: 9999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(56, 189, 248, 0.4); }

section[data-testid="stSidebar"] {
    background: rgba(17, 24, 39, 0.7);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
section[data-testid="stSidebar"] h2 { 
    color: #CBD5E1; 
    font-size: 0.75rem; 
    text-transform: uppercase; 
    letter-spacing: 0.05em; 
    font-weight: 600; 
}

/* ---------------------------------------------------
   UTILITY CLASSES (SaaS Components)
   --------------------------------------------------- */

.hero-card {
    background: linear-gradient(135deg, rgba(26, 36, 56, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
}

.glass-card {
    background: rgba(26, 36, 56, 0.45);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
}

.metric-card {
    background: rgba(26, 36, 56, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15), 0 2px 4px -1px rgba(0, 0, 0, 0.08);
}

.analytics-card {
    background: linear-gradient(180deg, rgba(26, 36, 56, 0.6) 0%, rgba(17, 24, 39, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.action-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 1.25rem;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.action-card:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(56, 189, 248, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.status-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    background: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.02em;
}

.section-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #F8FAFC;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.timeline-card {
    border-left: 2px solid rgba(56, 189, 248, 0.3);
    padding-left: 1.5rem;
    margin-left: 0.5rem;
    position: relative;
    padding-bottom: 1.5rem;
}
.timeline-card::before {
    content: '';
    position: absolute;
    left: -0.35rem;
    top: 0.25rem;
    width: 0.6rem;
    height: 0.6rem;
    background: #38BDF8;
    border-radius: 50%;
    box-shadow: 0 0 0 4px #0F172A;
}
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
def save_database():
    save_data(st.session_state.db)

def save_brain():
    save_data(st.session_state.db)

def save_gap():
    save_data(st.session_state.db)

def save_mission():
    save_data(st.session_state.db)

def save_day_log():
    save_data(st.session_state.db)

def save_interview():
    save_data(st.session_state.db)

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

# ==================== TIMER HELPERS ====================
def start_timer(start_key, running_key, result_key=None):
    st.session_state[start_key] = datetime.now()
    st.session_state[running_key] = True
    if result_key:
        st.session_state[result_key] = None

def stop_timer(start_key, running_key, result_key=None):
    if st.session_state.get(running_key) and start_key in st.session_state:
        elapsed = get_elapsed_time(st.session_state[start_key])
        if result_key:
            mins = int(elapsed) // 60
            secs = int(elapsed) % 60
            st.session_state[result_key] = f"{mins}m {secs}s"
        st.session_state[running_key] = False

def pause_timer(running_key):
    if running_key in st.session_state:
        st.session_state[running_key] = False

def resume_timer(running_key):
    if running_key in st.session_state:
        st.session_state[running_key] = True

def reset_timer(start_key, running_key, result_key=None):
    st.session_state.pop(start_key, None)
    if result_key:
        st.session_state.pop(result_key, None)
    st.session_state[running_key] = False

def get_elapsed_time(start_val, in_minutes=False):
    if not start_val:
        return 0
    if isinstance(start_val, str):
        start_val = datetime.strptime(start_val, "%Y-%m-%d %H:%M:%S")
    elapsed = (datetime.now() - start_val).total_seconds()
    return int(elapsed / 60) if in_minutes else elapsed

def get_remaining_time(elapsed_minutes, total_minutes):
    return max(0, total_minutes - elapsed_minutes)

def get_progress(elapsed, total):
    if total <= 0: return 0
    return min(100, int((elapsed / total) * 100))

# ==================== RUNTIME FRAGMENTS ====================
@st.fragment
def gap_timer_component():
    st.markdown("### ⏱️ Practice Timer")
    col_gt1, col_gt2, col_gt3 = st.columns(3)
    with col_gt1:
        if st.button("▶️ Start Timer", key="start_gap_timer"):
            start_timer("gap_timer_start", "gap_timer_running", "gap_timer_result")
    with col_gt2:
        if st.button("⏹️ Stop Timer", key="stop_gap_timer"):
            stop_timer("gap_timer_start", "gap_timer_running", "gap_timer_result")
    with col_gt3:
        if st.button("🔄 Reset Timer", key="reset_gap_timer"):
            reset_timer("gap_timer_start", "gap_timer_running", "gap_timer_result")

    if st.session_state.get("gap_timer_result"):
        st.info(f"⏱️ Time taken to solve: {st.session_state.gap_timer_result}")

@st.fragment
def mock_timer_component():
    st.markdown("### ⏱️ Timer")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        if st.button("▶️ Start", key="start_timer"):
            start_timer("timer_start", "timer_running", "timer_result")
    with col_t2:
        if st.button("⏹️ Stop", key="stop_timer"):
            stop_timer("timer_start", "timer_running", "timer_result")
    with col_t3:
        if st.button("🔄 Reset", key="reset_timer"):
            reset_timer("timer_start", "timer_running", "timer_result")

    if st.session_state.get("timer_result"):
        mins_taken = int(st.session_state.timer_result.split("m")[0])
        st.info(f"⏱️ Time taken: {st.session_state.timer_result}")
        if mins_taken >= 20:
            st.warning("Over 20 minutes — flag this topic for extra practice.")

# ==================== SESSION STATE ====================
def initialize_session():
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

initialize_session()

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
        save_mission()

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
    
    # Time and Greeting Setup
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    hour = now.hour
    today_name = now.strftime("%A")
    formatted_date = now.strftime("%B %d, %Y")

    if hour < 12: greeting = "Good Morning ☀️"
    elif hour < 17: greeting = "Good Afternoon 🌤️"
    else: greeting = "Good Evening 🌙"

    gap_log_h = st.session_state.db["gap_log"]
    day_logs_h = st.session_state.db["day_logs"]
    problem_count = len([e for e in gap_log_h if e.get("type") == "gap_entry"])
    weak_count = len({e["topic"] for e in gap_log_h if e.get("type") == "gap_entry" and e.get("score", 0) <= 1})
    day_count = len(day_logs_h)

    # SECTION 1: Large Hero Card
    brain = st.session_state.brain
    recommended_topic = brain.get("recommended_topic")

    if recommended_topic:
        recommendation_text = f"Your highest priority right now is <strong>{recommended_topic}</strong>. Strengthen this topic before moving on."
        status_label = "AI Recommendation"
    elif brain["current_focus"]:
        recommendation_text = f"Continue working on your active focus: <strong>{brain['current_focus']}</strong>."
        status_label = "Current Focus"
    elif mission and mission["status"] == MISSION_PENDING:
        recommendation_text = f"Start today's queued mission: <strong>{mission['title']}</strong>."
        status_label = "Queued Mission"
    else:
        recommendation_text = "Clear skies! Generate a new GapFinder problem to keep improving."
        status_label = "Status"

    active_mission_title = mission["title"] if mission else "No Active Mission"
    progress_val = mission["progress"] if mission else 0
    mission_status = mission["status"].title() if mission else "None"
    current_focus_val = brain.get("current_focus") if brain.get("current_focus") else "None"

    # Command Bar UI Variables
    cmd_current_module = st.session_state.current_page
    cmd_current_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%H:%M IST")
    
    cmd_status_map = {
        "Dashboard": "Monitoring",
        "GapFinder": "Gap Analysis",
        "Study Chat": "Assistant Ready",
        "FlowState": "Deep Focus",
        "Mock Interview": "Interview Mode"
    }
    cmd_ai_status = "Active"
    for mod_key, mod_status in cmd_status_map.items():
        if mod_key.lower() in str(cmd_current_module).lower():
            cmd_ai_status = mod_status
            break

    # Premium Dashboard Command Center Layout
    
    
    # Premium Live Command Bar -> Redesigned as Dynamic Live Activity Feed
    m_status_lower = str(mission_status).lower()
    if "complete" in m_status_lower:
        mission_segment = "🎯 Mission Complete"
    elif "active" in m_status_lower or "progress" in m_status_lower or "started" in m_status_lower:
        mission_segment = "🎯 Mission Active"
    else:
        mission_segment = "🎯 Mission Ready"

    mod_lower = str(cmd_current_module).lower()
    if "chat" in mod_lower or "interview" in mod_lower:
        ai_segment = "🤖 AI Coaching"
    elif "gap" in mod_lower or "analytics" in mod_lower or "health" in mod_lower:
        ai_segment = "🤖 AI Analyzing"
    else:
        ai_segment = "🤖 AI Monitoring"

    st.markdown(f"""
    <style>
    .os-container {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        white-space: nowrap;
        overflow-x: auto;
        font-size: 0.85rem;
        width: 100%;
        box-sizing: border-box;
        gap: 0.75rem;
    }}
    .os-segment {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.85rem;
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        color: #a8a29e;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .os-segment:hover {{
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 255, 255, 0.08);
        box-shadow: 0 0 14px rgba(255, 255, 255, 0.06);
        color: #ffffff;
    }}
    .os-segment-highlight {{
        color: #ffffff;
        font-weight: 600;
    }}
    @keyframes status-pulse {{
        0% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.5); }}
        70% {{ transform: scale(1.1); box-shadow: 0 0 0 6px rgba(74, 222, 128, 0); }}
        100% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }}
    }}
    .pulse-dot {{
        width: 7px;
        height: 7px;
        background-color: #4ade80;
        border-radius: 50%;
        display: inline-block;
        animation: status-pulse 2s infinite;
    }}
    </style>

    <div class="os-container">
        <div class="os-segment os-segment-highlight">🧠 NexusAI</div>
        <div class="os-segment">📍 Dashboard</div>
        <div class="os-segment">{mission_segment}</div>
        <div class="os-segment" style="gap: 0.65rem;">
            {ai_segment}
            <span class="pulse-dot"></span>
        </div>
        <div class="os-segment">🕒 {cmd_current_time}</div>
    </div>
    """, unsafe_allow_html=True)
    
    h_col1, h_col2 = st.columns([3, 2])
    
    with h_col1:
        st.markdown(f"""
        <h1 style="margin: 0 0 0.25rem 0; font-size: 2.25rem; font-weight: 700; color: #ffffff;">{greeting}</h1>
        <p style="color: #a8a29e; font-size: 1.05rem; margin: 0 0 1.5rem 0;">Ready to continue your Software Engineering journey?</p>
        
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600; margin-bottom: 0.35rem;">Current AI Status</div>
            <div style="font-size: 0.95rem; color: #f5f1ec; background: rgba(255,255,255,0.02); border-radius: 6px; padding: 0.75rem 1rem; border: 1px solid rgba(255,255,255,0.04);">{recommendation_text}</div>
        </div>
        <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600; margin-bottom: 0.15rem;">Current Focus</div>
            <div style="font-size: 1rem; color: #ffffff; font-weight: 600;">{current_focus_val}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with h_col2:
        st.markdown(f"""
        <div style="text-align: right; margin-bottom: 1.5rem;">
            <span class="status-chip" style="margin: 0;">{today_name}</span>
            <p style="color: #a8a29e; margin: 0.35rem 0 0 0; font-size: 0.95rem; font-weight: 500;">{formatted_date}</p>
        </div>
        <div style="background: rgba(0,0,0,0.15); border-radius: 8px; padding: 1.25rem; border: 1px solid rgba(255,255,255,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600;">Mission Status</span>
                <span class="status-chip" style="margin: 0;">{mission_status}</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; margin-bottom: 0.35rem;">
                    <span>Mission Progress</span>
                    <span style="font-weight: 600; color: #b77a48;">{progress_val}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.progress(progress_val / 100)
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.25rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.05); margin-bottom: 1.25rem;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600;">Recommended Topic</span>
                <span class="status-chip" style="background: rgba(183, 122, 72, 0.15); color: #d9985c; border-color: rgba(183, 122, 72, 0.3); margin: 0;">{recommended_topic if recommended_topic else "Optimal"}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Routing Action Button (now inside the card)
        if recommended_topic:
            if st.button(f"🎯 Route to GapFinder to Practice {recommended_topic}", key="hero_route_gap", use_container_width=True):
                st.session_state.brain["current_focus"] = recommended_topic
                set_page("🎯 GapFinder")
                st.rerun()
        elif mission and mission["status"] == MISSION_PENDING:
            if st.button("🚀 Start Current Mission", key="hero_start_mission", use_container_width=True):
                mission["status"] = MISSION_ACTIVE
                mission["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_mission()
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True) # Closes inner right-side card
        
    

    # BOTTOM ROW: Four Premium Mini Information Cards
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    
    with b_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 500;">📚 Problems Solved</div>
            <div style="font-size: 1.75rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;">{problem_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #d9985c; font-weight: 500;">🎯 Weak Topics</div>
            <div style="font-size: 1.75rem; font-weight: 700; color: #d9985c; margin-top: 0.25rem;">{weak_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 500;">📅 Study Days</div>
            <div style="font-size: 1.75rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;">{day_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 500;">⚡ Active Mission</div>
            <div style="font-size: 1.05rem; font-weight: 600; color: #ffffff; margin-top: 0.4rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{active_mission_title}">{active_mission_title}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    

    # SECTION 2: Live Intelligence Metrics
    st.write("")
    
    # Pre-compute metric states and logic
    prob_caption = "Start solving problems" if problem_count == 0 else "Growing steadily"
    day_caption = "No sessions yet" if day_count == 0 else "Building Habit"
    
    if weak_count == 0:
        health_text = "Excellent"
        health_color = "#10b981"
        health_icon = "🟢"
    elif weak_count <= 2:
        health_text = "Stable"
        health_color = "#f59e0b"
        health_icon = "🟡"
    else:
        health_text = "Needs Attention"
        health_color = "#ef4444"
        health_icon = "🔴"

    confidence = max(0, min(100, problem_count * 8 + day_count * 6 - weak_count * 5))
    if confidence >= 75:
        conf_label = "Strong"
        conf_color = "#10b981"
    elif confidence >= 50:
        conf_label = "Improving"
        conf_color = "#3b82f6"
    elif confidence >= 25:
        conf_label = "Learning"
        conf_color = "#f59e0b"
    else:
        conf_label = "Beginner"
        conf_color = "#a8a29e"

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    with m_col1:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.25rem 1rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600;">Problems Solved</span>
                <span style="font-size: 1rem;">📚</span>
            </div>
            <div style="font-size: 1.85rem; font-weight: 700; color: #ffffff; line-height: 1;">{problem_count}</div>
            <div style="font-size: 0.8rem; color: #a8a29e; font-weight: 500;">{prob_caption}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.25rem 1rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600;">Knowledge Health</span>
                <span style="font-size: 1rem;">🎯</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 700; color: {health_color}; line-height: 1.2; display: flex; align-items: center; gap: 0.4rem;">
                <span style="font-size: 0.9rem;">{health_icon}</span> {health_text}
            </div>
            <div style="font-size: 0.8rem; color: #a8a29e; font-weight: 500;">{weak_count} weak topic(s) logged</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.25rem 1rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600;">Study Consistency</span>
                <span style="font-size: 1rem;">📅</span>
            </div>
            <div style="font-size: 1.85rem; font-weight: 700; color: #ffffff; line-height: 1;">{day_count} <span style="font-size: 0.9rem; font-weight: 500; color: #a8a29e;">days</span></div>
            <div style="font-size: 0.8rem; color: #a8a29e; font-weight: 500;">{day_caption}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.25rem 1rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a8a29e; font-weight: 600;">AI Confidence</span>
                <span style="font-size: 1rem;">⚡</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <div style="font-size: 1.85rem; font-weight: 700; color: #ffffff; line-height: 1;">{confidence}%</div>
                <div style="font-size: 0.8rem; font-weight: 600; color: {conf_color};">{conf_label}</div>
            </div>
            <div style="width: 100%; background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden; margin-top: 0.2rem;">
                <div style="width: {confidence}%; background: {conf_color}; height: 100%; border-radius: 3px; transition: width 0.5s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")

    # SECTION 3: Mission Intelligence
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 600; color: #ffffff;">🎯 Mission Intelligence</h2>
        <p style="color: #a8a29e; margin: 0.25rem 0 0 0; font-size: 0.95rem;">AI-generated task based on your learning performance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if mission:
        priority = mission.get("priority", 100)
        if priority >= 90:
            p_chip = '<span class="status-chip" style="background: rgba(220, 38, 38, 0.15); color: #ef4444; border-color: rgba(220, 38, 38, 0.3);">🔥 High Priority</span>'
        elif priority >= 60:
            p_chip = '<span class="status-chip" style="background: rgba(217, 119, 6, 0.15); color: #f59e0b; border-color: rgba(217, 119, 6, 0.3);">⚡ Medium Priority</span>'
        else:
            p_chip = '<span class="status-chip" style="background: rgba(13, 148, 136, 0.15); color: #14b8a6; border-color: rgba(13, 148, 136, 0.3);">📌 Low Priority</span>'

        if mission["status"] == MISSION_ACTIVE and mission["started_at"]:
            elapsed_seconds = get_elapsed_time(mission["started_at"])
            total_seconds = mission["duration"] * 60
            mission["progress"] = get_progress(elapsed_seconds, total_seconds)

        # Simplified Single Premium Glass Card
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.75rem; margin-bottom: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.05); background: rgba(255, 255, 255, 0.02); border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                <h3 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #ffffff;">{mission["title"]}</h3>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    {p_chip}
                    <span class="status-chip" style="margin: 0;">{mission["status"].title()}</span>
                </div>
            </div>
            <p style="color: #a8a29e; margin: 0 0 1.25rem 0; font-size: 0.95rem; line-height: 1.6;">{mission["reason"]}</p>
            <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #a8a29e; font-weight: 500; margin-bottom: 1.5rem; padding-bottom: 1.25rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                <span>⏱️ Duration: <strong style="color: #ffffff;">{mission["duration"]} Minutes</strong></span>
            </div>
        """, unsafe_allow_html=True)
        
        # Full-Width Action Button Inside Card
        if mission["status"] == MISSION_PENDING:
            if st.button("▶ Start Mission", key="dash_start_mission", use_container_width=True):
                mission["status"] = MISSION_ACTIVE
                mission["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_mission()
                st.rerun()
        elif mission["status"] == MISSION_ACTIVE:
            if st.button("✅ Complete Mission", key="dash_complete_mission", use_container_width=True):
                mission["status"] = MISSION_COMPLETED
                mission["progress"] = 100
                mission["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.db["current_mission"] = None
                save_mission()
                st.rerun()
        else:
            st.button("✅ Completed", key="dash_mission_done", disabled=True, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="glass-card" style="padding: 4rem 2rem; text-align: center; border: 1px dashed rgba(255,255,255,0.15);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <h3 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1.5rem;">No Active Mission</h3>
            <p style="color: #a8a29e; font-size: 1rem; max-width: 450px; margin: 0 auto 2rem auto;">NexusAI automatically creates missions based on GapFinder performance.</p>
        """, unsafe_allow_html=True)
        
        emp_col1, emp_col2, emp_col3 = st.columns([1, 1.5, 1])
        with emp_col2:
            if st.button("Generate Practice Problem", key="dash_generate_gapfinder", use_container_width=True):
                set_page("🎯 GapFinder")
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")


    # SECTION 4: Intelligence Framework Matrix
    st.markdown('<div class="section-title" style="margin-top: 2rem; margin-bottom: 1.5rem; font-size: 1.5rem; font-weight: 600; color: #ffffff;">📊 Intelligence Framework Matrix</div>', unsafe_allow_html=True)
    
    db = st.session_state.db
    gap_log = [e for e in db["gap_log"] if e.get("type") == "gap_entry"]
    day_logs = db["day_logs"]
    weak_entries = [e for e in gap_log if e.get("score", 0) <= 1]

    # Pre-compute topic scores and weak metrics
    topic_scores = {}
    for e in gap_log:
        topic = e["topic"]
        if topic not in topic_scores:
            topic_scores[topic] = []
        topic_scores[topic].append(e.get("score", 0))

    topic_data = {}
    for e in weak_entries:
        topic = e["topic"]
        if topic not in topic_data:
            topic_data[topic] = {"attempts": 0, "last_attempt": e["date"]}
        topic_data[topic]["attempts"] += 1
        if e["date"] > topic_data[topic]["last_attempt"]:
            topic_data[topic]["last_attempt"] = e["date"]

    # --- GRID ROW 1: Top Left & Top Right ---
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        # TOP LEFT: Weak Topics
        html_weak = '<div class="analytics-card" style="height: 100%; min-height: 320px; box-sizing: border-box; padding: 1.5rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 1.5rem;">'
        html_weak += '<h4 style="margin-top: 0; margin-bottom: 1.25rem; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">🎯 Weak Topics</h4>'
        
        if weak_entries:
            # Sort topics by attempt count descending and take top 5
            sorted_weak = sorted(topic_data.items(), key=lambda x: x[1]["attempts"], reverse=True)[:5]
            for topic, data in sorted_weak:
                avg_score = sum(topic_scores[topic]) / len(topic_scores[topic])
                if avg_score <= 0.5:
                    status_badge = '<span class="status-chip" style="background: rgba(220, 38, 38, 0.15); color: #ef4444; border-color: rgba(220, 38, 38, 0.3); margin: 0;">Critical</span>'
                elif avg_score < 1.0:
                    status_badge = '<span class="status-chip" style="background: rgba(217, 119, 6, 0.15); color: #f59e0b; border-color: rgba(217, 119, 6, 0.3); margin: 0;">Improving</span>'
                else:
                    status_badge = '<span class="status-chip" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); margin: 0;">Stable</span>'
                
                html_weak += f"""
                <div style="padding: 0.85rem 1rem; background: rgba(255,255,255,0.015); border-radius: 8px; margin-bottom: 0.6rem; border: 1px solid rgba(255,255,255,0.04); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #f5f1ec; font-size: 0.95rem;">{topic}</div>
                        <div style="font-size: 0.8rem; color: #a8a29e; margin-top: 0.2rem;">{data['attempts']} weak attempt(s)</div>
                    </div>
                    <div>{status_badge}</div>
                </div>
                """
        else:
            html_weak += """
            <div style="text-align: center; padding: 3rem 1rem; color: #a8a29e;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✨</div>
                <div style="font-size: 0.95rem; font-weight: 500; color: #ffffff;">No Weak Topics Tracked</div>
                <div style="font-size: 0.85rem; margin-top: 0.25rem;">All your recent practice scores are optimal.</div>
            </div>
            """
        html_weak += '</div>'
        st.markdown(html_weak, unsafe_allow_html=True)

    with row1_col2:
        # TOP RIGHT: Learning Analytics
        html_matrix = '<div class="analytics-card" style="height: 100%; min-height: 320px; box-sizing: border-box; padding: 1.5rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 1.5rem;">'
        html_matrix += '<h4 style="margin-top: 0; margin-bottom: 1.25rem; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">📈 Learning Analytics</h4>'
        
        if gap_log:
            html_matrix += '<div style="display: grid; grid-template-columns: 1fr; gap: 0.6rem;">'
            for topic, scores in topic_scores.items():
                avg = sum(scores) / len(scores)
                bar = "🟢" if avg >= 1.5 else "🟡" if avg >= 0.8 else "🔴"
                
                html_matrix += f"""
                <div style="padding: 0.85rem 1rem; background: rgba(255,255,255,0.015); border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 0.65rem;">
                        <span style="font-size: 1.1rem;">{bar}</span>
                        <div>
                            <div style="font-weight: 600; color: #f5f1ec; font-size: 0.95rem;">{topic}</div>
                            <div style="font-size: 0.75rem; color: #a8a29e; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.15rem;">{len(scores)} Total Attempts</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">{avg:.1f} <span style="font-weight: 400; color: #a8a29e; font-size: 0.85rem;">/ 2.0</span></div>
                        <div style="font-size: 0.75rem; color: #a8a29e;">Avg Score</div>
                    </div>
                </div>
                """
            html_matrix += '</div>'
        else:
            html_matrix += """
            <div style="text-align: center; padding: 3rem 1rem; color: #a8a29e;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-size: 0.95rem; font-weight: 500; color: #ffffff;">No Analytics Available</div>
                <div style="font-size: 0.85rem; margin-top: 0.25rem;">Practice code concepts via side modules to populate KPIs.</div>
            </div>
            """
        html_matrix += '</div>'
        st.markdown(html_matrix, unsafe_allow_html=True)

    # --- GRID ROW 2: Bottom Left & Bottom Right ---
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        # BOTTOM LEFT: Retest Queue
        html_queue = '<div class="analytics-card" style="height: 100%; min-height: 320px; box-sizing: border-box; padding: 1.5rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 1.5rem;">'
        html_queue += '<h4 style="margin-top: 0; margin-bottom: 1.25rem; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">⏰ Retest Queue</h4>'
        
        if topic_data:
            for topic, data in topic_data.items():
                days_since = (datetime.now().date() - datetime.strptime(data["last_attempt"], "%Y-%m-%d").date()).days
                if days_since >= 7:
                    badge = '<span class="status-chip" style="background: rgba(220, 38, 38, 0.15); color: #ef4444; border-color: rgba(220, 38, 38, 0.3); margin: 0;">🔴 Due Now</span>'
                    subtext = f"Overdue by {days_since - 7} day(s)" if days_since > 7 else "Scheduled for today"
                else:
                    badge = f'<span class="status-chip" style="background: rgba(217, 119, 6, 0.15); color: #f59e0b; border-color: rgba(217, 119, 6, 0.3); margin: 0;">🟡 In {7 - days_since} days</span>'
                    subtext = f"Last practiced {days_since} day(s) ago"
                
                html_queue += f"""
                <div style="padding: 0.85rem 1rem; background: rgba(255,255,255,0.015); border-radius: 8px; margin-bottom: 0.6rem; border: 1px solid rgba(255,255,255,0.04); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #f5f1ec; font-size: 0.95rem;">{topic}</div>
                        <div style="font-size: 0.8rem; color: #a8a29e; margin-top: 0.2rem;">{subtext}</div>
                    </div>
                    <div>{badge}</div>
                </div>
                """
        else:
            html_queue += """
            <div style="text-align: center; padding: 3rem 1rem; color: #a8a29e;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏳</div>
                <div style="font-size: 0.95rem; font-weight: 500; color: #ffffff;">Queue is Empty</div>
                <div style="font-size: 0.85rem; margin-top: 0.25rem;">No topics are currently scheduled for retesting.</div>
            </div>
            """
        html_queue += '</div>'
        st.markdown(html_queue, unsafe_allow_html=True)

    with row2_col2:
        # BOTTOM RIGHT: Recent Study Sessions
        html_sessions = '<div class="analytics-card" style="height: 100%; min-height: 320px; box-sizing: border-box; padding: 1.5rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 1.5rem;">'
        html_sessions += '<h4 style="margin-top: 0; margin-bottom: 1.25rem; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">📅 Recent Study Sessions</h4>'
        
        if day_logs:
            for log in reversed(day_logs[-5:]):
                html_sessions += f"""
                <div style="padding: 0.85rem 1rem; background: rgba(255,255,255,0.015); border-radius: 8px; margin-bottom: 0.6rem; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                        <span style="font-weight: 600; color: #ffffff; font-size: 0.95rem;">{log['completed']}</span>
                        <span style="font-size: 0.75rem; color: #a8a29e; background: rgba(255,255,255,0.03); padding: 0.2rem 0.5rem; border-radius: 4px; white-space: nowrap;">{log['date']}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #a8a29e; line-height: 1.4;">{log['review']}</div>
                </div>
                """
        else:
            html_sessions += """
            <div style="text-align: center; padding: 3rem 1rem; color: #a8a29e;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📖</div>
                <div style="font-size: 0.95rem; font-weight: 500; color: #ffffff;">No Study Logs Found</div>
                <div style="font-size: 0.85rem; margin-top: 0.25rem;">Your completed study intervals will appear here.</div>
            </div>
            """
        html_sessions += '</div>'
        st.markdown(html_sessions, unsafe_allow_html=True)

    st.write("")

    # SECTION 5: Command Dock
    st.markdown('<div class="section-title" style="margin-top: 2rem; margin-bottom: 1.5rem; font-size: 1.5rem; font-weight: 600; color: #ffffff;">⚡ Command Dock</div>', unsafe_allow_html=True)
    
    qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
    
    with qa_col1:
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem 1rem; text-align: center; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 0.75rem; height: 200px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; box-sizing: border-box;">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">💬</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.35rem;">Study Chat</div>
                <div style="font-size: 0.8rem; color: #a8a29e; line-height: 1.4; margin-bottom: 1rem; min-height: 36px; display: flex; align-items: center; justify-content: center;">AI-powered interactive learning tutor.</div>
            </div>
            <div>
                <span class="status-chip" style="background: rgba(13, 148, 136, 0.15); color: #14b8a6; border-color: rgba(13, 148, 136, 0.3); margin: 0; font-size: 0.75rem;">Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Study Chat", key="qa_study_chat", use_container_width=True):
            set_page("💬 Study Chat")
            st.rerun()

    with qa_col2:
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem 1rem; text-align: center; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 0.75rem; height: 200px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; box-sizing: border-box;">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">🎯</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.35rem;">GapFinder</div>
                <div style="font-size: 0.8rem; color: #a8a29e; line-height: 1.4; margin-bottom: 1rem; min-height: 36px; display: flex; align-items: center; justify-content: center;">Diagnose and repair knowledge gaps.</div>
            </div>
            <div>
                <span class="status-chip" style="background: rgba(217, 119, 6, 0.15); color: #f59e0b; border-color: rgba(217, 119, 6, 0.3); margin: 0; font-size: 0.75rem;">Practice</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Practice Now", key="qa_practice_weak", use_container_width=True):
            if recommended_topic:
                st.session_state.brain["current_focus"] = recommended_topic
            set_page("🎯 GapFinder")
            st.rerun()

    with qa_col3:
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem 1rem; text-align: center; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 0.75rem; height: 200px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; box-sizing: border-box;">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">⚡</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.35rem;">FlowState</div>
                <div style="font-size: 0.8rem; color: #a8a29e; line-height: 1.4; margin-bottom: 1rem; min-height: 36px; display: flex; align-items: center; justify-content: center;">Deep focus timer & study ambient.</div>
            </div>
            <div>
                <span class="status-chip" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); margin: 0; font-size: 0.75rem;">Focus</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Resume Focus", key="qa_resume_flow", use_container_width=True):
            set_page("⚡ FlowState")
            st.rerun()

    with qa_col4:
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem 1rem; text-align: center; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 0.75rem; height: 200px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; box-sizing: border-box;">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">🎤</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.35rem;">Mock Interview</div>
                <div style="font-size: 0.8rem; color: #a8a29e; line-height: 1.4; margin-bottom: 1rem; min-height: 36px; display: flex; align-items: center; justify-content: center;">Simulate technical & behavior rounds.</div>
            </div>
            <div>
                <span class="status-chip" style="background: rgba(220, 38, 38, 0.15); color: #ef4444; border-color: rgba(220, 38, 38, 0.3); margin: 0; font-size: 0.75rem;">Interview</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Interview", key="qa_start_interview", use_container_width=True):
            set_page("🎤 Mock Interview")
            st.rerun()
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
                    save_gap()
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

                start_timer("focus_start", "focus_running")

                brain["last_activity"] = "Started Focus Session"

                save_brain()

                st.success("Focus session started.")

        with col2:

            if st.button(

                "⏸ Pause",

                use_container_width=True,

                key="focus_pause_btn"

            ):

                pause_timer("focus_running")

                brain["last_activity"] = "Paused Focus Session"

                st.warning("Focus paused.")

        with col3:

            if st.button(

                "✅ Complete",

                use_container_width=True,

                key="focus_complete_btn"

            ):

                elapsed = get_elapsed_time(st.session_state.get("focus_start"), in_minutes=True)

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

                save_database()

                stop_timer("focus_start", "focus_running")

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

                save_day_log()

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

                total_focus = get_elapsed_time(st.session_state.focus_start, in_minutes=True)

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

        elif mission["status"] == MISSION_COMPLETED:

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

                    save_mission()

                    st.success(
                        "New mission generated."
                    )

                    st.rerun()

    # ==========================================================
    # AUTO SAVE
    # ==========================================================

    save_database()

    # ==========================================================
    # FLOWSTATE FOOTER
    # ==========================================================

    st.divider()

    st.caption(
        "FlowState synchronizes your mission, AI Brain, study plans and daily progress automatically."
    )

elif st.session_state.current_page == "🎤 Mock Interview":

    st.session_state.brain["current_module"] = "Mock Interview"

    section_header(
        "🎤",
        "Mock Interview",
        "Practice interviews at the real hiring bar.",
        "#7A3F3F"
    )

    brain = st.session_state.brain

    db = st.session_state.db

    gap_log = [
        e
        for e in db["gap_log"]
        if e.get("type") == "gap_entry"
    ]

    weak_topics = sorted(
        list(
            set(
                e["topic"]
                for e in gap_log
                if e.get("score",0) <= 1
            )
        )
    )

    if weak_topics:

        st.warning(
            "⚠ Recommended Weak Topics: "
            + ", ".join(weak_topics)
        )

    mission = db.get("current_mission")

    st.markdown("## 🎯 Interview Control Center")

    interview_card = st.container(border=True)

    with interview_card:

        col1,col2 = st.columns(2)

        with col1:

            company = st.selectbox(

                "Company Type",

                [

                    "FAANG",

                    "Product Company",

                    "Startup",

                    "Service Company"

                ],

                key="mock_company"

            )

            role = st.selectbox(

                "Target Role",

                [

                    "SDE-1",

                    "SDE-2"

                ],

                key="mock_role"

            )

        with col2:

            topic = st.selectbox(

                "Interview Topic",

                [

                    "Prefix Sum",

                    "Sliding Window",

                    "Contribution Technique",

                    "Bit Manipulation",

                    "2D Matrices",

                    "Strings"

                ],

                index=0,

                key="mock_topic"

            )

            difficulty = st.selectbox(

                "Difficulty",

                [

                    "Easy",

                    "Medium",

                    "Hard"

                ],

                index=1,

                key="mock_difficulty"

            )

    st.write("")

    st.markdown("## 🧠 AI Interview Context")

    context_card = st.container(border=True)

    with context_card:

        c1,c2,c3 = st.columns(3)

        with c1:

            st.metric(

                "Current Focus",

                brain.get("current_focus") or "None"

            )

        with c2:

            st.metric(

                "Recommended",

                brain.get("recommended_topic") or "None"

            )

        with c3:

            if mission:

                st.metric(

                    "Mission",

                    mission["status"].title()

                )

            else:

                st.metric(

                    "Mission",

                    "None"

                )

    st.write("")

    st.markdown("## 🚀 Start Interview")

    if st.button(

        "Generate Interview",

        use_container_width=True,

        key="generate_interview_btn"

    ):

        brain["last_activity"] = "Started Mock Interview"

        brain["current_focus"] = topic

        prompt = f"""
You are a Senior Software Engineer interviewing for a {company}.

Role:
{role}

Difficulty:
{difficulty}

Topic:
{topic}

Generate ONE interview question.

Format:

# Question

# Constraints

# Example

# What Interviewers Expect

Do NOT provide any hints or solutions.
"""

        with st.spinner(

            "Preparing interview..."

        ):

            response = client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[

                    {

                        "role":"system",

                        "content":"You are a senior interviewer."

                    },

                    {

                        "role":"user",

                        "content":prompt

                    }

                ]

            )

        st.session_state.mock_question = (

            response

            .choices[0]

            .message

            .content

        )

        
        st.success(

            "Interview generated."

        )

    st.write("")
    # ==========================================================
    # LIVE INTERVIEW
    # ==========================================================

    if "mock_question" in st.session_state:

        st.markdown("## 💼 Live Interview")

        interview_container = st.container(border=True)

        with interview_container:

            st.markdown(st.session_state.mock_question)

            st.info(
                f"""
**Company:** {st.session_state.mock_company}

**Role:** {st.session_state.mock_role}

**Difficulty:** {st.session_state.mock_difficulty}

**Topic:** {st.session_state.mock_topic}
"""
            )

        st.write("")

        st.markdown("## ⏱ Interview Timer")

        timer_container = st.container(border=True)

        with timer_container:

            interview_time = st.selectbox(

                "Interview Duration",

                [

                    20,

                    30,

                    45,

                    60

                ],

                index=1,

                key="mock_duration"

            )

            c1,c2,c3 = st.columns(3)

            with c1:

                if st.button(

                    "▶ Start Interview",

                    use_container_width=True,

                    key="mock_start_btn"

                ):

                    start_timer("mock_start", "mock_running")

                    brain["last_activity"] = "Interview Started"

                    st.success(
                        "Interview timer started."
                    )

            with c2:

                if st.button(

                    "⏸ Pause",

                    use_container_width=True,

                    key="mock_pause_btn"

                ):

                    pause_timer("mock_running")

                    brain["last_activity"] = "Interview Paused"

                    st.warning(
                        "Interview paused."
                    )

            with c3:

                if st.button(

                    "⏹ End Interview",

                    use_container_width=True,

                    key="mock_stop_btn"

                ):

                    stop_timer("mock_start", "mock_running")

                    brain["last_activity"] = "Interview Finished"

                    st.success(
                        "Interview ended."
                    )

        if st.session_state.get("mock_running"):

            elapsed = get_elapsed_time(st.session_state.mock_start, in_minutes=True)

            remaining = get_remaining_time(elapsed, interview_time)

            progress = get_progress(elapsed, interview_time)

            st.progress(

                progress

            )

            left,right = st.columns(2)

            with left:

                st.metric(

                    "Elapsed",

                    f"{elapsed} min"

                )

            with right:

                st.metric(

                    "Remaining",

                    f"{remaining} min"

                )

            if remaining == 0:

                st.warning(
                    "Interview time is over."
                )

        st.write("")
            # ==========================================================
    # CANDIDATE WORKSPACE
    # ==========================================================

    if "mock_question" in st.session_state:

        st.markdown("## 👨‍💻 Candidate Workspace")

        workspace = st.container(border=True)

        with workspace:

            clarification = st.text_area(

                "Clarification Questions (optional)",

                placeholder="What would you ask the interviewer before coding?",

                height=100,

                key="mock_clarification"

            )

            brute_force = st.text_area(

                "Brute Force Approach",

                placeholder="Explain your first solution.",

                height=150,

                key="mock_bruteforce"

            )

            optimal = st.text_area(

                "Optimal Approach",

                placeholder="Explain your optimized solution.",

                height=180,

                key="mock_optimal"

            )

            col1, col2 = st.columns(2)

            with col1:

                time_complexity = st.text_input(

                    "Time Complexity",

                    placeholder="O(n)",

                    key="mock_time"

                )

            with col2:

                space_complexity = st.text_input(

                    "Space Complexity",

                    placeholder="O(1)",

                    key="mock_space"

                )

            final_code = st.text_area(

                "Final Code",

                placeholder="Paste your Java / Python / C++ solution here.",

                height=300,

                key="mock_code"

            )

        st.write("")

        ready = (
            len(optimal.strip()) > 15
            and len(final_code.strip()) > 20
        )

        if ready:

            st.success(
                "✅ Solution ready for evaluation."
            )

        else:

            st.info(
                "Complete the optimal approach and final code before submitting."
            )

        st.write("")

        st.markdown("## 📦 Submission")

        submit_container = st.container(border=True)

        with submit_container:

            if st.button(

                "🚀 Submit Interview",

                use_container_width=True,

                key="mock_submit"

            ):

                if not ready:

                    st.warning(
                        "Complete your solution before submitting."
                    )

                else:

                    brain["last_activity"] = "Submitted Mock Interview"

                    st.session_state.mock_submission = {

                        "company": st.session_state.mock_company,

                        "role": st.session_state.mock_role,

                        "difficulty": st.session_state.mock_difficulty,

                        "topic": st.session_state.mock_topic,

                        "clarification": clarification,

                        "bruteforce": brute_force,

                        "optimal": optimal,

                        "time": time_complexity,

                        "space": space_complexity,

                        "code": final_code

                    }

                    st.success(
                        "Interview submitted successfully."
                    )

        st.write("")
            # ==========================================================
    # SENIOR ENGINEER EVALUATION
    # ==========================================================

    if "mock_submission" in st.session_state:

        st.markdown("## 🧑‍⚖️ Senior Engineer Evaluation")

        evaluation_container = st.container(border=True)

        with evaluation_container:

            if st.button(

                "📝 Evaluate Interview",

                use_container_width=True,

                key="evaluate_mock_btn"

            ):

                submission = st.session_state.mock_submission

                evaluation_prompt = f"""
You are a Senior Software Engineer conducting a final interview evaluation.

Interview Details

Company:
{submission['company']}

Role:
{submission['role']}

Difficulty:
{submission['difficulty']}

Topic:
{submission['topic']}

Interview Question

{st.session_state.mock_question}

Candidate Clarification Questions

{submission['clarification']}

Brute Force Approach

{submission['bruteforce']}

Optimal Approach

{submission['optimal']}

Time Complexity

{submission['time']}

Space Complexity

{submission['space']}

Final Code

{submission['code']}

Evaluate like a real senior interviewer.

Return exactly in this format.

# Problem Understanding
Score /10

# Communication
Score /10

# Algorithm Selection
Score /10

# Optimization
Score /10

# Time Complexity
Score /10

# Space Complexity
Score /10

# Code Quality
Score /10

# Edge Cases
Score /10

# Overall Feedback

# Final Verdict

Choose ONLY one:

Strong Hire

Hire

Lean Hire

Lean No Hire

No Hire

Do not be generous.
"""

                with st.spinner(

                    "Senior engineer evaluating..."

                ):

                    response = client.chat.completions.create(

                        model="llama-3.1-8b-instant",

                        messages=[

                            {

                                "role":"system",

                                "content":"You are a senior software engineer interviewer. Be extremely honest."

                            },

                            {

                                "role":"user",

                                "content":evaluation_prompt

                            }

                        ]

                    )

                evaluation = (

                    response

                    .choices[0]

                    .message

                    .content

                )

                st.session_state.mock_evaluation = evaluation

        if "mock_evaluation" in st.session_state:

            st.markdown("### 📋 Interview Report")

            report = st.container(border=True)

            with report:

                st.markdown(

                    st.session_state.mock_evaluation

                )

            verdict = "Unknown"

            report_text = st.session_state.mock_evaluation

            if "Strong Hire" in report_text:

                verdict = "Strong Hire"

            elif "\nHire" in report_text:

                verdict = "Hire"

            elif "Lean Hire" in report_text:

                verdict = "Lean Hire"

            elif "Lean No Hire" in report_text:

                verdict = "Lean No Hire"

            elif "No Hire" in report_text:

                verdict = "No Hire"

            if verdict == "Strong Hire":

                st.success("🏆 Strong Hire")

            elif verdict == "Hire":

                st.success("✅ Hire")

            elif verdict == "Lean Hire":

                st.info("👍 Lean Hire")

            elif verdict == "Lean No Hire":

                st.warning("⚠️ Lean No Hire")

            else:

                st.error("❌ No Hire")

        st.write("")
            # ==========================================================
    # SAVE INTERVIEW
    # ==========================================================

    if "mock_evaluation" in st.session_state:

        st.markdown("## 💾 Save Interview")

        save_container = st.container(border=True)

        with save_container:

            if st.button(

                "Save Interview",

                use_container_width=True,

                key="save_mock_interview"

            ):

                evaluation = st.session_state.mock_evaluation

                verdict = "Unknown"

                if "Strong Hire" in evaluation:
                    verdict = "Strong Hire"
                elif "Lean Hire" in evaluation:
                    verdict = "Lean Hire"
                elif "Lean No Hire" in evaluation:
                    verdict = "Lean No Hire"
                elif "\nHire" in evaluation:
                    verdict = "Hire"
                elif "No Hire" in evaluation:
                    verdict = "No Hire"

                interview_record = {

                    "date": datetime.now().strftime("%Y-%m-%d"),

                    "company": st.session_state.mock_company,

                    "role": st.session_state.mock_role,

                    "difficulty": st.session_state.mock_difficulty,

                    "topic": st.session_state.mock_topic,

                    "verdict": verdict,

                    "evaluation": evaluation

                }

                if "mock_history" not in st.session_state.db:

                    st.session_state.db["mock_history"] = []

                st.session_state.db["mock_history"].append(
                    interview_record
                )

                brain["last_activity"] = "Completed Mock Interview"

                brain["current_focus"] = None

                update_recommended_topic()

                save_interview()

                st.success(
                    "Interview saved successfully."
                )

    st.write("")

    # ==========================================================
    # INTERVIEW ANALYTICS
    # ==========================================================

    st.markdown("## 📊 Interview Analytics")

    analytics = st.container(border=True)

    with analytics:

        history = st.session_state.db.get(
            "mock_history",
            []
        )

        total = len(history)

        strong = sum(
            1
            for x in history
            if x["verdict"] == "Strong Hire"
        )

        hire = sum(
            1
            for x in history
            if x["verdict"] == "Hire"
        )

        lean_hire = sum(
            1
            for x in history
            if x["verdict"] == "Lean Hire"
        )

        nohire = sum(
            1
            for x in history
            if x["verdict"] in [
                "Lean No Hire",
                "No Hire"
            ]
        )

        c1,c2,c3,c4 = st.columns(4)

        with c1:

            st.metric(
                "Interviews",
                total
            )

        with c2:

            st.metric(
                "Hire+",
                strong + hire
            )

        with c3:

            st.metric(
                "Lean Hire",
                lean_hire
            )

        with c4:

            st.metric(
                "No Hire",
                nohire
            )

    st.write("")

    # ==========================================================
    # RECENT INTERVIEWS
    # ==========================================================

    history = st.session_state.db.get(
        "mock_history",
        []
    )

    if history:

        st.markdown("## 📜 Recent Interviews")

        for interview in reversed(history[-5:]):

            with st.expander(

                f"{interview['date']} • {interview['company']} • {interview['verdict']}"

            ):

                st.write(
                    f"**Role:** {interview['role']}"
                )

                st.write(
                    f"**Difficulty:** {interview['difficulty']}"
                )

                st.write(
                    f"**Topic:** {interview['topic']}"
                )

                st.markdown("---")

                st.markdown(
                    interview["evaluation"]
                )

    st.write("")

    # ==========================================================
    # DASHBOARD SYNC
    # ==========================================================

    update_recommended_topic()

    save_database()

    st.divider()

    st.caption(
        "Mock Interview automatically synchronizes with your AI Brain, Dashboard and Mission Engine."
    )
