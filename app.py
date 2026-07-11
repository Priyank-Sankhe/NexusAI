import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="NexusAI", layout="wide")
st.title("NexusAI 🧠")
st.subheader("Your personal AI study operating system")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "gap_log" not in st.session_state:
    st.session_state.gap_log = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "flow_plan" not in st.session_state:
    st.session_state.flow_plan = None
if "checkin_done" not in st.session_state:
    st.session_state.checkin_done = False

tab1, tab2, tab3 = st.tabs(["💬 Study Chat", "🎯 GapFinder", "⚡ FlowState"])

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

with tab2:
    st.header("GapFinder 🎯")
    st.caption("Get a problem, solve it, get evaluated. Weakness tracked automatically.")

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
            problem_prompt = f"""Generate a DSA problem specifically on the topic: {selected_topic}.
            The problem MUST test {selected_topic} concepts only.
            
            Format exactly like this:
            PROBLEM: [problem statement with example input and output]
            DIFFICULTY: [Easy/Medium]
            HINT: [one line hint, not the solution]"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are a DSA problem generator. Generate problems specifically about {selected_topic} only."},
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
            "Write your approach here — pseudocode, logic, or actual code:",
            height=200,
            key="solution_input"
        )

        if st.button("Evaluate My Solution"):
            if user_solution.strip():
                with st.spinner("Evaluating..."):
                    eval_prompt = f"""Problem: {st.session_state.current_problem}

Student's solution attempt: {user_solution}

IMPORTANT: If the solution attempt is empty, less than 10 characters,
is more than 10 characters but completely irrelevant to the topic
or is a question rather than a solution attempt, respond only with:
"Please write an actual solution attempt before requesting evaluation."
Do not evaluate, do not generate a solution.

If it is a genuine attempt, evaluate strictly:
1. CORRECT: What did they get right?
2. MISSING: What's wrong or missing?
3. OPTIMAL SOLUTION: Show the correct approach with explanation
4. SCORE: Rate 0 (wrong), 1 (partial), or 2 (correct)
5. VERDICT: "Move on" or "Review this topic" """

                    eval_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict but fair DSA interviewer evaluating a student's solution."},
                            {"role": "user", "content": eval_prompt}
                        ]
                    )
                    evaluation = eval_response.choices[0].message.content
                    st.markdown("### Evaluation")
                    st.markdown(evaluation)

                    st.session_state.gap_log.append({
                        "topic": st.session_state.current_topic,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "evaluation": evaluation
                    })
            else:
                st.warning("Write your solution before evaluating.")

with tab3:
    st.header("FlowState ⚡")
    st.caption("3PM–11PM study window | Check-in every 4 hours | Set phone alarms at 3PM and 7PM")

    # Morning Planning (show if no plan exists for today)
    today = datetime.now().strftime("%Y-%m-%d")

    st.markdown("### 📋 Daily Planning")
    
    priority1 = st.text_input("Priority 1 (most important):", placeholder="e.g. Cold-solve sliding window")
    priority2 = st.text_input("Priority 2:", placeholder="e.g. Module 5 Day 51 with notes")
    priority3 = st.text_input("Priority 3:", placeholder="e.g. Project build - GapFinder tab")
    hours_available = st.slider("Hours available today:", 1, 8, 6)

    # Pull weak topics from GapFinder log
    weak_topics = []
    for log in st.session_state.gap_log:
        if "Review this topic" in log.get("evaluation", ""):
            weak_topics.append(log["topic"])

    if st.button("Generate My Plan"):
        if priority1:
            with st.spinner("Building your day..."):
                weak_context = f"Weak topics flagged by GapFinder: {', '.join(set(weak_topics))}" if weak_topics else "No weak topics flagged yet."
                
                plan_prompt = f"""You are a strict study planner for a software engineering student.

Study window: 3PM to 11PM today ({hours_available} hours available)
Check-ins at: 7PM and 11PM

Today's priorities:
1. {priority1}
2. {priority2 if priority2 else 'Not specified'}
3. {priority3 if priority3 else 'Not specified'}

{weak_context}

Generate a specific hour-by-hour plan from 3PM to 11PM.
Be realistic — include short breaks.
Flag which priority is most critical if time runs short.
End with: MOST CRITICAL TASK TODAY: [one task]"""

                plan_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a strict, realistic study planner. No fluff. Specific time blocks only."},
                        {"role": "user", "content": plan_prompt}
                    ]
                )
                st.session_state.flow_plan = plan_response.choices[0].message.content
                st.session_state.flow_date = today
        else:
            st.warning("Enter at least Priority 1 before generating.")

    if st.session_state.flow_plan:
        st.markdown("### Your Plan")
        st.markdown(st.session_state.flow_plan)

        # 4-hour Check-in
        st.markdown("---")
        st.markdown("### ⏰ 7PM Check-in")
        checkin_report = st.text_area(
            "What actually happened since 3PM? Be honest:",
            placeholder="e.g. Completed priority 1, got distracted for 1 hour, didn't start priority 2",
            height=100
        )

        if st.button("Replan Rest of Day"):
            if checkin_report.strip():
                with st.spinner("Replanning..."):
                    replan_prompt = f"""Original plan: {st.session_state.flow_plan}

What actually happened since 3PM: {checkin_report}

It is now 7PM. 4 hours remain (7PM-11PM).
Generate a revised plan for 7PM-11PM only.
Be realistic about what's still achievable.
Protect the most critical task above everything else.
If everything is on track, say so and confirm the original plan for the remaining hours."""

                    replan_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict replanner. Adapt to reality, protect the most critical task."},
                            {"role": "user", "content": replan_prompt}
                        ]
                    )
                    st.markdown("### Revised Plan (7PM-11PM)")
                    st.markdown(replan_response.choices[0].message.content)
            else:
                st.warning("Report what happened before replanning.")

        # End of day log
        st.markdown("---")
        st.markdown("### 🌙 11PM End of Day")
        eod_report = st.text_area(
            "What did you complete today?",
            placeholder="e.g. Priority 1 done, Priority 2 half done, Priority 3 skipped",
            height=100
        )

        if st.button("Log Day & Get Tomorrow's Focus"):
            if eod_report.strip():
                with st.spinner("Logging..."):
                    eod_prompt = f"""Today's plan: {st.session_state.flow_plan}
                    
What was completed: {eod_report}

Give:
1. COMPLETION RATE: Estimate % of planned work done
2. WHAT TO CARRY FORWARD: Uncompleted tasks for tomorrow
3. TOMORROW'S FOCUS: Single most important thing for tomorrow based on today
4. HONEST ASSESSMENT: One sentence on today's execution — no sugarcoating"""

                    eod_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a strict but fair daily reviewer. Honest assessment only."},
                            {"role": "user", "content": eod_prompt}
                        ]
                    )
                    st.markdown("### Day Review")
                    st.markdown(eod_response.choices[0].message.content)
                    
                    # Log to shared data layer
                    st.session_state.gap_log.append({
                        "type": "day_log",
                        "date": today,
                        "completed": eod_report,
                        "review": eod_response.choices[0].message.content
                    })
            else:
                st.warning("Report what you completed before logging.")
