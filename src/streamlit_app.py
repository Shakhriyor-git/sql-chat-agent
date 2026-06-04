import sys
import os

# Add project root to path so 'src' is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.agent import ask_agent

# Page config
st.set_page_config(page_title="SQL Chat Agent", page_icon="💬")

# Title
st.title("💬 SQL Chat Agent")
st.caption("Ask questions about credit risk data in plain English")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about borrowers, defaults, income..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_agent(prompt)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})