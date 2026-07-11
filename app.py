import streamlit as st
from groq import Groq

st.set_page_config(page_title="NexusAI", layout="wide")
st.title("NexusAI 🧠")
st.subheader("Your personal AI study operating system")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": system_context},
                        *st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })

with tab2:
    st.header("GapFinder")
    st.write("Coming next...")

with tab3:
    st.header("FlowState")
    st.write("Coming next...")
