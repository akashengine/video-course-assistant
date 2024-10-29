# app.py

import streamlit as st
import openai
from thread_manager import ThreadManager

# Initialize the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Define the assistant ID
ASSISTANT_ID = "asst_FsFGT6vkPNt1ATj1axikkIzT"

# Initialize the ThreadManager with the assistant ID
thread_manager = ThreadManager(ASSISTANT_ID)

# Initialize Streamlit session state for threads
if "active_thread" not in st.session_state:
    st.session_state.active_thread = None  # Currently selected thread
if "threads" not in st.session_state:
    st.session_state.threads = {}  # Dictionary to store thread IDs and names

# Sidebar for thread management
st.sidebar.title("Chat Threads")

# Button to create a new thread
if st.sidebar.button("New Thread"):
    # Create a new thread and set it as the active thread
    new_thread_id = thread_manager.create_thread()
    st.session_state.threads[new_thread_id] = f"Thread {len(st.session_state.threads) + 1}"
    st.session_state.active_thread = new_thread_id

# Dropdown to select an active thread
selected_thread_id = st.sidebar.selectbox("Select a Thread", list(st.session_state.threads.keys()), format_func=lambda x: st.session_state.threads[x])
if selected_thread_id:
    st.session_state.active_thread = selected_thread_id

# Display the name of the active thread
st.write(f"**Active Thread**: {st.session_state.threads[st.session_state.active_thread]}")

# Sidebar inputs for selecting Video ID, Language, and Request Type
video_id = st.sidebar.text_input("Video ID", value="312")  # Default video ID for test
