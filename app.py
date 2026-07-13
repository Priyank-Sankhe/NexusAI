import streamlit as st
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import threading
import copy

st.set_page_config(page_title="NexusAI", layout="wide")
st.markdown("""

""", unsafe_allow_html=True)

# ==================== CONFIG ====================

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
BIN_ID = st.secrets["JSONBIN_BIN_ID"]
MASTER_KEY = st.secrets["JSONBIN_MASTER_KEY"]
JSONBIN_URL = f"[https://api.jsonbin.io/v3/b/](https://www.google.com/search?q=https://api.jsonbin.io/v3/b/){BIN_ID}"

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

{icon} {title}
{subtitle}

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

```
if st.session_state.get("gap_timer_result"):
    st.info(f"⏱️ Time taken to solve: {st.session_state.gap_timer_result}")

```

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

```
if st.session_state.get("timer_result"):
    mins_taken = int(st.session_state.timer_result.split("m")[0])
    st.info(f"⏱️ Time taken: {st.session_state.timer_result}")
    if mins_taken >= 20:
        st.warning("Over 20 minutes — flag this topic for extra practice.")

```

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

```
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

```

# ==================== RENDER COMPONENT CONTROLLERS ====================

if st.session_state.current_page == "📊 Dashboard":
st.session_state.brain["current_module"] = "Dashboard"

```
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
        <div style="width: 100%; background: rgba(255,255,255,10); height: 6px; border-radius: 3px; overflow: hidden; margin-top: 0.2rem;">
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

```

elif st.session_state.current_page == "💬 Study Chat":
st.session_state.brain["current_module"] = "Study Chat"
section_header("💬", "Study Chat", "Ask anything about your Scaler journey. NexusAI remembers your learning context.", "#385C7A")

```
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

```

STUDENT PROFILE:

* Name: Shivang
* Program: Scaler Academy Software Development Program
* Current module: Module 5 (AI & Agents)
* Completed: Java basics, intermediate DSA (arrays, prefix sum, carry forward, contribution technique, sliding window, bit manipulation, 2D matrices, strings)
* Background: Career switcher, non-CS degree, learning from scratch
* Target: 18 LPA software development role
* Known weak areas: sliding window, contribution technique (not yet cold-solved)
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

* Concise and focused — no padding
* Bold key terms on first use
* End complex explanations with a verification question
SCOPE: Only answer questions about software engineering, DSA, Java, Python, system design, Scaler curriculum, career strategy, and AI/ML from Module 5. Redirect anything outside this scope."""
```
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

```



elif st.session_state.current_page == "🎯 GapFinder":
st.session_state.brain["current_module"] = "GapFinder"

```
```
# --- BACKEND DATA & VARIABLE RETRIEVAL (UNMODIFIED) ---
weak_topics = get_weak_topics(st.session_state.db["gap_log"])
weak_topic_names = list(set([w['topic'] for w in weak_topics])) if weak_topics else []
weak_topics_str = ', '.join(weak_topic_names) if weak_topic_names else "None"

topics = ["Prefix Sum", "Sliding Window", "Contribution Technique", "Bit Manipulation", "2D Matrices", "Strings"]
recommended = st.session_state.brain.get("recommended_topic")
default_index = 0
if recommended in topics: 
    default_index = topics.index(recommended)
    
current_focus_val = st.session_state.brain.get("current_focus") if st.session_state.brain.get("current_focus") else "None"

# --- PREMIUM CURSOR-INSPIRED NAVY STYLING INJECTION ---
st.markdown("""
<style>
.gf-header {
    background: linear-gradient(135deg, #0B0F19 0%, #111827 100%);
    border: 1px solid rgba(56, 189, 248, 0.08);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.gf-panel {
    background: #0F172A;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
}
.gf-metric-box {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.04);
    padding: 10px 16px;
    border-radius: 8px;
    min-width: 140px;
}
.gf-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
    font-weight: 700;
    margin-bottom: 4px;
}
.gf-val {
    font-size: 0.95rem;
    color: #F8FAFC;
    font-weight: 600;
}
.badge-pill {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
.code-container {
    background: #090D16;
    border: 1px solid rgba(255, 255, 255, 0.04);
    padding: 12px;
    border-radius: 8px;
    color: #E2E8F0;
    font-family: ui-monospace, monospace;
    font-size: 0.88rem;
    white-space: pre-wrap;
}
.eval-card {
    background: linear-gradient(135deg, #0B132B 0%, #0F172A 100%);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
}
.eval-section-title {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
    margin-bottom: 8px;
    margin-top: 16px;
}
.history-row {
    background: rgba(15, 23, 42, 0.6);
    border-left: 3px solid rgba(56, 189, 248, 0.4);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
            align-items: center;
}
</style>
""", unsafe_allow_html=True)

# --- GAPFINDER HEADER ---
st.markdown("""
<div class="gf-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em;">🎯 GapFinder</h2>
            <p style="color: #64748B; margin: 4px 0 0 0; font-size: 0.9rem;">Deliberate practice environment engineered for rapid technical consensus.</p>
        </div>
        <div style="display: flex; gap: 12px;">
            <div class="gf-metric-box">
                <div class="gf-label">Current Focus</div>
                <div class="gf-val" style="color: #E2E8F0;">""" + str(current_focus_val) + """</div>
            </div>
            <div class="gf-metric-box">
                <div class="gf-label">Recommended Topic</div>
                <div class="gf-val" style="color: #38BDF8;">""" + str(recommended if recommended else "None") + """</div>
            </div>
            <div class="gf-metric-box">
                <div class="gf-label">Weak Topics Due</div>
                <div class="gf-val" style="color: #F87171;">""" + str(len(weak_topic_names)) + """</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TOPIC SELECTION ROW ---
sel_col1, sel_col2 = st.columns([3, 1])
with sel_col1:
    selected_topic = st.selectbox("Select Core Track Topic", topics, index=default_index, key="gap_topic", label_visibility="collapsed")
with sel_col2:
    generate_clicked = st.button("Generate Problem", key="gen_problem", use_container_width=True, type="primary")

# Handle Logic for Generation Trigger (UNMODIFIED BUSINESS LOGIC)
if generate_clicked:
    st.session_state.brain["current_focus"] = selected_topic
    st.session_state.brain["last_activity"] = "Generated a practice problem"
    with st.spinner("Compiling tactical problem profile..."):
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

# --- MAIN WORKSPACE ---
if "current_problem" in st.session_state:
    raw_problem = st.session_state.current_problem
    lines = raw_problem.split('\n')
    
    prob_statement = ""
    difficulty = "Medium"
    hint_text = ""
    example_text = ""
    
    for line in lines:
        cleaned = line.strip()
        if cleaned.startswith("PROBLEM:"):
            prob_statement = cleaned.replace("PROBLEM:", "").strip()
        elif cleaned.startswith("DIFFICULTY:"):
            difficulty = cleaned.replace("DIFFICULTY:", "").strip()
        elif cleaned.startswith("HINT:"):
            hint_text = cleaned.replace("HINT:", "").strip()
        elif "Example" in cleaned or "EXAMPLE:" in cleaned:
            example_text += cleaned + "\n"
        else:
            if cleaned and not any(cleaned.startswith(prefix) for prefix in ["PROBLEM:", "DIFFICULTY:", "HINT:"]):
                prob_statement += "\n" + cleaned

    diff_color = "#34D399" if "Easy" in difficulty else "#FBBF24"
    diff_bg = "rgba(52, 211, 153, 0.1)" if "Easy" in difficulty else "rgba(251, 191, 36, 0.1)"
    diff_border = "rgba(52, 211, 153, 0.2)" if "Easy" in difficulty else "rgba(251, 191, 36, 0.2)"
    est_time = "15 mins" if "Easy" in difficulty else "30 mins"

    ws_col_left, ws_col_right = st.columns(2)

    with ws_col_left:
        st.markdown("""
        <div class="gf-panel" style="min-height: 520px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="margin: 0 0 14px 0; color: #F8FAFC; font-size: 1.05rem; font-weight: 600;">🎯 Challenge Overview</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px;">
                    <span class="badge-pill" style="background: rgba(56, 189, 248, 0.08); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.15);">Track: """ + str(st.session_state.current_topic) + """</span>
                    <span class="badge-pill" style="background: """ + diff_bg + """; color: """ + diff_color + """; border: 1px solid """ + diff_border + """;">""" + difficulty + """</span>
                    <span class="badge-pill" style="background: rgba(255, 255, 255, 0.04); color: #94A3B8; border: 1px solid rgba(255, 255, 255, 0.08);">⏱ """ + est_time + """</span>
                </div>
                <div style="margin-bottom: 16px;">
                    <div class="gf-label">Problem Statement</div>
                    <p style="color: #CBD5E1; line-height: 1.5; font-size: 0.92rem; margin: 4px 0 0 0; white-space: pre-wrap;">""" + str(prob_statement if prob_statement else raw_problem) + """</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if example_text:
            st.markdown("""
            <div style="margin-bottom: 16px;">
                <div class="gf-label">Example IO</div>
                <div class="code-container">""" + str(example_text.strip()) + """</div>
            </div>
            """, unsafe_allow_html=True)
            
        if hint_text:
            st.markdown("""
            <div>
                <div class="gf-label" style="color: #38BDF8;">💡 Strategy Hint</div>
                <p style="color: #94A3B8; font-style: italic; font-size: 0.88rem; margin: 2px 0 0 0;">""" + str(hint_text) + """</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with ws_col_right:
        st.markdown("""
        <div style="background: #0F172A; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 20px; min-height: 520px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; color: #F8FAFC; font-size: 1.05rem; font-weight: 600;">💻 Solution Workspace</h3>
                <span class="badge-pill" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.2);">JAVA</span>
            </div>
        """, unsafe_allow_html=True)
        
        user_solution = st.text_area(
            "Write your approach — pseudocode, logic, or actual code:", 
            height=410, 
            key="solution_input",
            placeholder="// Enter solution logic, algorithmic analysis or working code structures...",
            label_visibility="collapsed"
        )
        
        st.markdown("""
            <div style="color: #475569; font-size: 0.74rem; margin-top: 10px; font-weight: 500; text-align: right; letter-spacing: 0.02em;">Verified context boundary. Copilot compilation connected.</div>
        </div>
        """, unsafe_allow_html=True)

    # --- PRACTICE TIMER & METRICS STATUS PANEL ---
    st.markdown("""
    <div style="background: #0B0F19; border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 12px 20px; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="badge-pill" style="background: rgba(255, 255, 255, 0.04); color: #94A3B8; border: 1px solid rgba(255, 255, 255, 0.08);">📚 Track: """ + str(st.session_state.current_topic) + """</span>
            <span class="badge-pill" style="background: rgba(16, 185, 129, 0.08); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.15);">⚡ Pipeline Active</span>
            <span class="badge-pill" style="background: rgba(14, 165, 233, 0.08); color: #0EA5E9; border: 1px solid rgba(14, 165, 233, 0.15);">🧠 Copilot Active</span>
        </div>
        <div style="min-width: 200px;">
    """, unsafe_allow_html=True)
    gap_timer_component()
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- EVALUATE SOLUTION ACTION ---
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    eval_triggered = st.button("Evaluate My Solution", key="eval_solution", use_container_width=True, type="secondary")

    if eval_triggered:
        if len(user_solution.strip()) < 10:
            st.markdown("""
            <div style="padding: 12px 16px; border-radius: 8px; background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.2); color: #F59E0B; font-size: 0.88rem; font-weight: 500; margin-top: 12px;">
                ⚠️ Submission failed: Solution content falls below meaningful logic thresholds. Please expand your explanation.
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Streaming logic matrices into evaluation runner..."):
                eval_prompt = f"Problem: {st.session_state.current_problem}\n\nStudent's solution: {user_solution}\n\nEvaluate strictly:\n1. CORRECT: What did they get right?\n2. MISSING: What's wrong or missing?\n3. OPTIMAL SOLUTION: Show the correct approach\n4. SCORE: 0 (wrong), 1 (partial), 2 (correct) — number only\n5. VERDICT: \"Move on\" or \"Review this topic\"\n\nBe strict. Do not give 2 unless genuinely correct."
                eval_response = client.chat.completions.create(
                    model="llama-3.3-70b-specdec",
                    messages=[
                        {"role": "system", "content": "You are a strict DSA interviewer. Evaluate honestly."},
                        {"role": "user", "content": eval_prompt}
                    ]
                )
                evaluation = eval_response.choices[0].message.content

                # --- CORE SCORE CALCULATION (UNMODIFIED) ---
                score = 1
                for line in evaluation.split("\n"):
                    if "SCORE:" in line:
                        if "0" in line: score = 0
                        elif "2" in line: score = 2
                        break

                # --- PARSING HELPERS FOR METADATA CARDS ---
                def extract_section(text, current_marker, next_markers):
                    try:
                        start_idx = text.find(current_marker)
                        if start_idx == -1:
                            return "Data chunk missing from context stream."
                        start_idx += len(current_marker)
                        end_idx = len(text)
                        for marker in next_markers:
                            m_idx = text.find(marker, start_idx)
                            if m_idx != -1 and m_idx < end_idx:
                                end_idx = m_idx
                        return text[start_idx:end_idx].strip().strip("*: \n\r")
                    except:
                        return "Error parsing section data."

                correct_content = extract_section(evaluation, "CORRECT:", ["MISSING:", "OPTIMAL SOLUTION:", "SCORE:", "VERDICT:"])
                missing_content = extract_section(evaluation, "MISSING:", ["OPTIMAL SOLUTION:", "SCORE:", "VERDICT:", "CORRECT:"])
                optimal_content = extract_section(evaluation, "OPTIMAL SOLUTION:", ["SCORE:", "VERDICT:", "CORRECT:", "MISSING:"])

                # --- EVALUATION OUTPUT DISPLAY ---
                current_date = datetime.now().strftime("%Y-%m-%d")
                topic_name = st.session_state.current_topic

                score_title = "❌ Needs Improvement"
                score_color = "#EF4444"
                score_bg = "linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, #0F172A 100%)"
                score_border = "rgba(239, 68, 68, 0.25)"
                
                if score == 2:
                    score_title = "✅ Excellent Performance"
                    score_color = "#10B981"
                    score_bg = "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, #0F172A 100%)"
                    score_border = "rgba(16, 185, 129, 0.25)"
                elif score == 1:
                    score_title = "⚠️ Partial Solution Verified"
                    score_color = "#F59E0B"
                    score_bg = "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, #0F172A 100%)"
                    score_border = "rgba(245, 158, 11, 0.25)"

                st.markdown("""
                <div class="eval-card" style="background: """ + score_bg + """; border: 1px solid """ + score_border + """;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 14px; margin-bottom: 16px;">
                        <div>
                            <h3 style="margin: 0; color: #F8FAFC; font-size: 1.25rem; font-weight: 600;">🤖 NexusAI Architectural Audit</h3>
                            <div style="color: #64748B; font-size: 0.8rem; margin-top: 4px; font-family: monospace;">Execution Date: """ + current_date + """ | Track Sector: """ + topic_name + """</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.3rem; font-weight: 700; color: """ + score_color + """;">""" + score_title + """</div>
                            <div style="color: #94A3B8; font-size: 0.82rem; font-weight: 500; margin-top: 2px;">Composite Mark: """ + str(score) + """ / 2</div>
                        </div>
                    </div>

                    <div class="eval-section-title" style="color: #10B981;">✓ Validated Assertions</div>
                    <p style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.5; margin: 0 0 16px 0; white-space: pre-wrap;">""" + correct_content + """</p>

                    <div class="eval-section-title" style="color: #F59E0B;">⚠️ Gaps & Structural Flaws</div>
                    <p style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.5; margin: 0 0 16px 0; white-space: pre-wrap;">""" + missing_content + """</p>

                    <div class="eval-section-title" style="color: #38BDF8;">🚀 Target Structural Archetype</div>
                    <div class="code-container" style="margin-bottom: 20px;">""" + optimal_content + """</div>
                """, unsafe_allow_html=True)

                if score <= 1:
                    st.markdown("""
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.18); padding: 12px 16px; border-radius: 6px; color: #FCA5A5; font-size: 0.85rem; font-weight: 600; margin-bottom: 16px;">
                        📌 Recommendation: Retain target parameter loop. Review execution traces before standard milestone recycling.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: rgba(16I'm having a hard time fulfilling your request. Can I help you with something else instead?

