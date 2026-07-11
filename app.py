import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="NexusAI", layout="wide")
st.title("NexusAI 🧠")
st.subheader("Your personal AI study operating system")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

tab1, tab2, tab3 = st.tabs(["💬 Study Chat", "🎯 GapFinder", "⚡ FlowState"])

with tab1:
    st.header("Study Chat")
    st.caption("Ask anything about your curriculum. Powered by Gemini — no token limits.")
    
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
        engineering student at Scaler Academy. The student is currently in Module 5 
        (AI & Agents), has completed Modules 1-4 covering Java basics and intermediate DSA 
        (arrays, prefix sum, contribution technique, sliding window, bit manipulation, 
        2D matrices, strings). Target: 18 LPA software development role. 
        Teaching style: first principles, no hand-holding, direct and honest."""
        
        full_prompt = f"{system_context}\n\nStudent question: {user_input}"
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_content(full_prompt)
                st.write(response.text)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response.text
                })

with tab2:
    st.header("GapFinder")
    st.write("Coming next...")

with tab3:
    st.header("FlowState")
    st.write("Coming next...")
