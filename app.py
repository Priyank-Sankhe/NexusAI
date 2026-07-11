import streamlit as st

st.set_page_config(page_title="NexusAI", layout="wide")
st.title("NexusAI 🧠")
st.subheader("Your personal AI study operating system")

tab1, tab2, tab3 = st.tabs(["💬 Study Chat", "🎯 GapFinder", "⚡ FlowState"])

with tab1:
    st.write("Study Chat — coming soon")

with tab2:
    st.write("GapFinder — coming soon")

with tab3:
    st.write("FlowState — coming soon")
