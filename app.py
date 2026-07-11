import streamlit as st
from groq import Groq
import json
from datetime import datetime

st.set_page_config(page_title="NexusAI", layout="wide")
st.title("NexusAI 🧠")
st.subheader("Your personal AI study operating system")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Shared data layer
if "gap_log" not in st.session_state:
    st.session_state.gap_log = []

tab1, tab2, tab3 = st.tabs(["💬 Study Chat", "🎯 GapFinder", "⚡ FlowState"])

with tab1:
    st.header("Study Chat")
    st.caption("Ask anything about your curriculum. No token limits.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

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
            problem_prompt = f"""Generate a DSA problem on the topic: {selected_topic}.
            
            Format exactly like this:
            PROBLEM: [problem statement with example input and output]
            DIFFICULTY: [Easy/Medium]
            HINT: [one line hint, not the solution]"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a DSA problem generator for a software engineering student preparing for technical interviews."},
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

                    # Log to shared data layer
                    st.session_state.gap_log.append({
                        "topic": st.session_state.current_topic,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "evaluation": evaluation
                    })
            else:
                st.warning("Write your solution before evaluating.")

with tab3:
    st.header("FlowState ⚡")
    st.write("Coming next...")
