# app.py

import streamlit as st
import openai
import pandas as pd
from utils import load_video_titles, fetch_openai_response

# Load API key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = 1  # Initialize a session ID

# Load video titles
video_titles = load_video_titles("VideoTitle.csv")

# Sidebar for selecting Video ID, Language, and Type of Request
st.sidebar.title("Video Course Assistant")
video_id = st.sidebar.selectbox("Select Video ID", list(video_titles.keys()))
language = st.sidebar.selectbox("Select Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam"])
session_id = st.session_state.session_id

# Display Selection
st.markdown(f"### VIDEO ID: {video_id}")
st.markdown(f"### LANGUAGE: {language}")
st.markdown(f"### Session ID: {session_id}")

# Request Type Buttons
request_type = st.radio("Choose Request Type", ["Summarize", "Quiz Me", "Ask a Question"], horizontal=True)

# Chat Interface
st.markdown("### Chat Interface")
input_text = st.text_input("Type your message here...")

# Handle "Send" Button
if st.button("Send"):
    if input_text.strip():
        # Send request to OpenAI based on request type, video ID, and language
        response = fetch_openai_response(request_type, video_id, language, input_text)
        st.session_state.chat_history.append({"role": "user", "content": input_text})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Display chat history
    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            st.write(f"You: {entry['content']}")
        else:
            st.write(f"Assistant: {entry['content']}")

# Reset button to clear chat
if st.button("Reset Chat"):
    st.session_state.chat_history = []

