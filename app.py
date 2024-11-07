import os
import base64
import re
import json
import time
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title="Video Course Assistant", layout="wide")

from openai import AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv

# Assuming utils.client is configured correctly
from utils import client

# Constants
ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]
VIDEO_BASE_URL = "https://console.drishtiias.com/auth_panel/file_manager/library/video_player_tNv50qIN68G1zQpGG1wdXMUcnTCcrER8So"

# Helper function to initialize session state
def init_session_state():
    if "threads" not in st.session_state:
        st.session_state["threads"] = {}
    if "current_thread_id" not in st.session_state:
        st.session_state["current_thread_id"] = None
    if "tool_calls" not in st.session_state:
        st.session_state["tool_calls"] = {}
    if "in_progress" not in st.session_state:
        st.session_state["in_progress"] = False
    if "chat_log" not in st.session_state:
        st.session_state["chat_log"] = {}
    if "video_id" not in st.session_state:
        st.session_state["video_id"] = None
    if "language" not in st.session_state:
        st.session_state["language"] = None
    if "chat_mode" not in st.session_state:
        st.session_state["chat_mode"] = False

# [Previous helper functions remain the same...]
# [Keep all the existing functions like send_message, EventHandler, create_new_thread, etc.]

# UI layout
st.title("Video Course Assistant")

# Top bar layout with Video ID and Language
col1, col2 = st.columns([1, 1])
with col1:
    video_id = st.selectbox("Video ID", video_ids, index=video_ids.index("503"))
with col2:
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"])

# Display session information
st.write(f"**VIDEO ID**: {video_id}")
st.write(f"**LANGUAGE**: {language}")

# Add Video Player Section
st.write("### Video Player")
video_iframe = f'<iframe src="{VIDEO_BASE_URL}/{video_id}" width="100%" height="500" title="VideoIframe"></iframe>'
st.components.v1.html(video_iframe, height=520)

# Function buttons
col4, col5, col6, col7 = st.columns([1, 1, 1, 1])
if col4.button("Summarise"):
    user_input = f"Summarise the content of the video with ID {video_id} in {language}."
    create_new_thread(user_input)
    send_message(st.session_state["current_thread_id"], user_input)

if col5.button("Quiz Me"):
    user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
    create_new_thread(user_input)
    send_message(st.session_state["current_thread_id"], user_input)

if col6.button("Ask a Question"):
    if st.session_state.get("current_thread_id") is None or not st.session_state.get("chat_mode", False):
        initial_prompt = f"The user wants to ask questions about video ID {video_id} in {language}."
        create_new_thread(initial_prompt)
        st.session_state["video_id"] = video_id
        st.session_state["language"] = language
        st.session_state["chat_mode"] = True

if col7.button("Reset"):
    st.session_state["threads"].clear()
    st.session_state["current_thread_id"] = None
    st.session_state["chat_mode"] = False
    st.write("All threads reset.")

# Chat interface section
if st.session_state.get("chat_mode", False) and st.session_state["current_thread_id"]:
    st.write("### Chat with the Assistant")
    messages = st.session_state["threads"][st.session_state["current_thread_id"]]
    for message in messages:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

    with st.form(key='chat_form', clear_on_submit=True):
        user_message = st.text_input("Your message: Or Enter Quit", key="user_message_input")
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_message:
            if user_message.strip().lower() == "quit":
                st.session_state["chat_mode"] = False
                st.write("Chat ended.")
            else:
                prompt = f"Question about video ID {st.session_state['video_id']} in {st.session_state['language']}: {user_message}"
                send_message(st.session_state["current_thread_id"], prompt)

else:
    thread_ids = list(st.session_state["threads"].keys())
    selected_thread = st.selectbox("Select Thread", thread_ids, index=0) if thread_ids else None
    if selected_thread:
        st.session_state["current_thread_id"] = selected_thread
        st.write("### Conversation History")
        messages = st.session_state["threads"][selected_thread]
        for message in messages:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            else:
                st.write(f"**Assistant:** {message['content']}")
