import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import requests
import json

st.set_page_config(page_title="NexusAI", layout="wide")
st.title("NexusAI 🧠")
st.subheader("Your personal AI study operating system")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
BIN_ID = st.secrets["JSONBIN_BIN_ID"]
MASTER_KEY = st.secrets["JSONBIN_MASTER_KEY"]
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

# ---------- PERSISTENT STORAGE FUNCTIONS ----------
def load_data():
    try:
        response = requests.get(
            JSONBIN_URL,
            headers={"X-Master-Key": MASTER_KEY}
        )
        return response.json()["record"]
    except:
        return {"gap_log": [], "day_logs": []}

def save_data(data):
    try:
        requests.put(
            JSONBIN_URL,
            headers={
                "X-Master-Key": MASTER_KEY,
                "Content-Type": "application/json"
            },
            json=data
        )
    except:
        st.error("Failed to save data. Check your JSONBin credentials.")

# ---------- SPACED REPETITION LOGIC ----------
def get_weak_topics(gap_log):
    weak = []
    today = datetime.now().date()
    for entry in gap_log:
        if entry.get("type") == "gap_entry":
            score = entry.get("score", 2)
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            days_since = (today - entry_date).days
            if score <= 1 and days_since >= 7: 
                weak.append({
                    "topic": entry["topic"],
                    "days_since": days_since,
                    "score": score
                })
    return weak

# ---------- LOAD DATA ----------
if "db" not in st.session_state:
    st.session_state.db = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "flow_plan" not in st.session_state:
    st.session_state.flow_plan = None

tab1, tab2, tab3 = st.tabs(["💬 Study Chat", "🎯 GapFinder", "⚡ FlowState"])

# ==================== TAB 1: STUDY CHAT ====================
with tab1:
    st.header("Study Chat")
    st.caption("Ask anything about your curriculum. No token limits.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        system_context = """You are NexusAI, a personal study assistant for a software 
        engineering student at Scaler Academy. Currently in Module 5 (AI & Agents). 
        Completed: Java basics, intermediate DSA (arrays, prefix sum, contribution 
        technique, sliding window, bit manipulation, 2D matrices, strings). 
        Target: 18 LPA software development role. 
        Teaching style: first principles, direct, honest, no hand-holding."""

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
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })

# ==================== TAB 2: GAPFINDER ====================
with tab2:
    st.header("GapFinder 🎯")
    st.caption("Get a problem, solve it, get evaluated. Weakness tracked automatically.")

    # Show weak topics due for retest
    weak_topics = get_weak_topics(st.session_state.db["gap_log"])
    if weak_topics:
        st.warning(f"⚠️ Topics due for retest: {', '.join(set([w['topic'] for w in weak_topics]))}")

    topics = [
        "Prefix Sum",
        "Sliding Window",
        "Contribution Technique",
        "Bit Manipulation",
        "2D Matrices",
        "Strings"
    ]

    selected_topic = st.selectbox("Select a topic:", topics)

    if st.button("Generate Problem"):
        with st.spinner("Generating problem..."):
            problem_prompt = f"""Generate a DSA problem specifically and only on: {selected_topic}.
            Do not generate problems on any other topic.
            
            Format exactly like this:
            PROBLEM: [clear problem statement with example input and output]
            DIFFICULTY: [Easy/Medium]
            HINT: [one line hint, not the solution]"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are a DSA problem generator. You only generate problems about {selected_topic}. Never generate problems about other topics."},
                    {"role": "user", "content": problem_prompt}
                ]
            )
            st.session_state.current_problem = response.choices[0].message.content
            st.session_state.current_topic = selected_topic

    if "current_problem" in st.session_state:
        st.markdown("### Problem")
        st.markdown(st.session_state.current_problem)

        st.markdown("### Your Solution Approach")
        user_solution = st.text_area(
            "Write your approach — pseudocode, logic, or actual code:",
            height=200,
            key="solution_input"
        )

        if st.button("Evaluate My Solution"):
            if len(user_solution.strip()) < 10:
                st.warning("Write an actual solution attempt before evaluating.")
            else:
                with st.spinner("Evaluating..."):
                    eval_prompt = f"""Problem: {st.session_state.current_problem}

Student's solution: {user_solution}

Evaluate strictly and honestly:
1. CORRECT: What did they get right?
2. MISSING: What's wrong or missing?
3. OPTIMAL SOLUTION: Show the correct approach
4. SCORE: 0 (wrong), 1 (partial), 2 (correct) — output the number only on this line
5. VERDICT: "Move on" or "Review this topic"

Be strict. Do not give 2 unless the approach is genuinely correct."""

                    eval_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict DSA interviewer. Evaluate honestly. Never fabricate solutions the student didn't write."},
                            {"role": "user", "content": eval_prompt}
                        ]
                    )
                    evaluation = eval_response.choices[0].message.content
                    st.markdown("### Evaluation")
                    st.markdown(evaluation)

                    # Parse score
                    score = 1
                    for line in evaluation.split("\n"):
                        if "SCORE:" in line:
                            if "0" in line:
                                score = 0
                            elif "2" in line:
                                score = 2
                            break

                    # Save to persistent storage
                    st.session_state.db["gap_log"].append({
                        "type": "gap_entry",
                        "topic": st.session_state.current_topic,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "score": score,
                        "evaluation": evaluation
                    })
                    save_data(st.session_state.db)

                    if score <= 1:
                        st.error(f"⚠️ {st.session_state.current_topic} flagged as weak. Will resurface in 7 days.")
                    else:
                        st.success(f"✅ {st.session_state.current_topic} marked solid.")

# ==================== TAB 3: FLOWSTATE ====================
with tab3:
    st.header("FlowState ⚡")
    st.caption("3PM–11PM | Check-in at 7PM | End of day at 11PM")

    today = datetime.now().strftime("%Y-%m-%d")

    # Pull weak topics for plan context
    weak = get_weak_topics(st.session_state.db["gap_log"])
    weak_context = f"Weak topics due for retest: {', '.join(set([w['topic'] for w in weak]))}" if weak else "No weak topics flagged yet."

    st.markdown("### 📋 Morning Planning")
    priority1 = st.text_input("Priority 1 (most critical):", placeholder="e.g. Cold-solve sliding window")
    priority2 = st.text_input("Priority 2:", placeholder="e.g. Module 5 Day 51 notes")
    priority3 = st.text_input("Priority 3:", placeholder="e.g. NexusAI bug fixes")
    hours_available = st.slider("Hours available today:", 1, 8, 6)

    if st.button("Generate My Plan"):
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
If weak topics exist, schedule retest time for them.
End with: MOST CRITICAL TASK TODAY: [one task]"""

                plan_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a strict, realistic study planner. Specific time blocks only. No fluff."},
                        {"role": "user", "content": plan_prompt}
                    ]
                )
                st.session_state.flow_plan = plan_response.choices[0].message.content

    if st.session_state.flow_plan:
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

        if st.button("Replan 7PM-11PM"):
            if len(checkin_report.strip()) < 10:
                st.warning("Report what actually happened before replanning.")
            else:
                with st.spinner("Replanning..."):
                    replan_prompt = f"""Original plan: {st.session_state.flow_plan}

What happened since 3PM: {checkin_report}

It is 7PM. 4 hours remain.
Generate revised plan for 7PM-11PM only.
Protect the most critical task above everything else.
Be realistic about what's achievable in 4 hours."""

                    replan_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict replanner. Protect critical tasks. Be realistic."},
                            {"role": "user", "content": replan_prompt}
                        ]
                    )
                    st.markdown("### Revised Plan (7PM-11PM)")
                    st.markdown(replan_response.choices[0].message.content)

        st.markdown("---")
        st.markdown("### 🌙 11PM End of Day")
        eod_report = st.text_area(
            "What did you complete today?",
            placeholder="e.g. Priority 1 done, Priority 2 half done",
            height=100,
            key="eod"
        )

        if st.button("Log Day"):
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

                    eod_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict daily reviewer. Honest assessment only. No sugarcoating."},
                            {"role": "user", "content": eod_prompt}
                        ]
                    )
                    review = eod_response.choices[0].message.content
                    st.markdown("### Day Review")
                    st.markdown(review)

                    # Save to persistent storage
                    st.session_state.db["day_logs"].append({
                        "date": today,
                        "completed": eod_report,
                        "review": review
                    })
                    save_data(st.session_state.db)
                    st.success("✅ Day logged. See you tomorrow.")
