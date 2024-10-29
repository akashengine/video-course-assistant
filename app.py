import os
import base64
import re
import json
import time

import streamlit as st
from openai import AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv

# Assuming utils.client is configured correctly
from utils import client  # or set up the client as in your second code

# Set Streamlit page configuration
st.set_page_config(page_title="Video Course Assistant", layout="wide")

# Constants
ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]

# Helper function to initialize session state
def init_session_state():
    if "threads" not in st.session_state:
        st.session_state["threads"] = {}  # Dictionary to store multiple threads
    if "current_thread_id" not in st.session_state:
        st.session_state["current_thread_id"] = None
    if "tool_calls" not in st.session_state:
        st.session_state["tool_calls"] = {}
    if "in_progress" not in st.session_state:
        st.session_state["in_progress"] = False
    if "chat_log" not in st.session_state:
        st.session_state["chat_log"] = {}

# Initialize session state
init_session_state()

# Function to create a new thread and add the initial message
def create_new_thread(prompt):
    thread = client.beta.threads.create()
    thread_id = thread.id
    # Store the thread and its initial message
    st.session_state["threads"][thread_id] = [{"role": "user", "content": prompt}]
    st.session_state["current_thread_id"] = thread_id
    # Send the initial message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )
    return thread_id

# UI layout
st.title("Video Course Assistant")

# Top bar layout with Video ID, Language, and Session ID
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    video_id = st.text_input("Video ID", placeholder="Enter Video ID", value="503")
with col2:
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"])
with col3:
    session_id = st.text_input("Session ID", value="12")

# Display session information
st.write(f"**VIDEO ID**: {video_id}")
st.write(f"**LANGUAGE**: {language}")
st.write(f"**Session ID**: {session_id}")

# Initialize user_input to None
user_input = None

# Function buttons
col4, col5, col6, col7 = st.columns([1, 1, 1, 1])
if col4.button("Summarise"):
    user_input = f"Summarise the content of the video with ID {video_id} in {language}."
    create_new_thread(user_input)
if col5.button("Quiz Me"):
    user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
    create_new_thread(user_input)
if col6.button("Ask a Question"):
    question = st.text_input("Type your question here:")
    if question:
        user_input = question
        create_new_thread(user_input)
if col7.button("Reset"):
    st.session_state["threads"].clear()
    st.session_state["current_thread_id"] = None
    st.write("All threads reset.")

# Dropdown to select active thread
thread_ids = list(st.session_state["threads"].keys())
selected_thread = st.selectbox("Select Thread", thread_ids, index=0) if thread_ids else None
if selected_thread:
    st.session_state["current_thread_id"] = selected_thread

# EventHandler class to handle assistant events and tool functionality
# EventHandler class to handle assistant events and tool functionality
class EventHandler(AssistantEventHandler):
    def __init__(self, thread_id):
        super().__init__()  # Call the superclass's __init__ method
        self.thread_id = thread_id
        self.current_message = ""
        self.current_markdown = None
        self.chat_log = st.session_state["threads"][thread_id]
        self.tool_calls = st.session_state.get("tool_calls", {})
        
    @override
    def on_event(self, event):
        pass

    @override
    def on_text_created(self, text):
        self.current_message = ""
        with st.chat_message("Assistant"):
            self.current_markdown = st.empty()

    @override
    def on_text_delta(self, delta, snapshot):
        if snapshot.value:
            text_value = re.sub(
                r"\[(.*?)\]\s*\(\s*(.*?)\s*\)", "Download Link", snapshot.value
            )
            self.current_message = text_value
            self.current_markdown.markdown(self.current_message, True)

    @override
    def on_text_done(self, text):
        format_text = format_annotation(text)
        self.current_markdown.markdown(format_text, True)
        self.chat_log.append({"role": "assistant", "content": format_text})

    @override
    def on_tool_call_created(self, tool_call):
        # Handle tool calls if needed
        pass

    @override
    def on_tool_call_done(self, tool_call):
        # Handle tool call completion if needed
        pass


# Function to format annotations (from the second code)
def format_annotation(text):
    citations = []
    text_value = text.value
    for index, annotation in enumerate(text.annotations):
        text_value = text_value.replace(annotation.text, f" [{index}]")

        if hasattr(annotation, "file_citation"):
            file_citation = annotation.file_citation
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(
                f"[{index}] {file_citation.quote} from {cited_file.filename}"
            )
        elif hasattr(annotation, "file_path"):
            file_path = annotation.file_path
            link_tag = create_file_link(
                annotation.text.split("/")[-1],
                file_path.file_id,
            )
            text_value = re.sub(r"\[(.*?)\]\s*\(\s*(.*?)\s*\)", link_tag, text_value)
    if citations:
        text_value += "\n\n" + "\n".join(citations)
    return text_value

# Function to create file links (from the second code)
def create_file_link(file_name, file_id):
    content = client.files.content(file_id)
    content_type = content.response.headers["content-type"]
    b64 = base64.b64encode(content.text.encode(content.encoding)).decode()
    link_tag = f'<a href="data:{content_type};base64,{b64}" download="{file_name}">Download Link</a>'
    return link_tag

# Function to send message to assistant
def send_message(thread_id, prompt):
    # Send message to the assistant in the specified thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )
    
    # Append the user message to the session state
    st.session_state["threads"][thread_id].append({"role": "user", "content": prompt})
    st.write(f"**You:** {prompt}")
    
    # Initialize EventHandler
    event_handler = EventHandler(thread_id)
    
    # Create a new run and stream with event handler
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
        event_handler=event_handler,
    ) as stream:
        stream.until_done()
    
    # Update the conversation history
    st.session_state["threads"][thread_id] = event_handler.chat_log

# If there's user input, send it to the assistant
if user_input and st.session_state["current_thread_id"]:
    send_message(st.session_state["current_thread_id"], user_input)

# Display the conversation history for the selected thread
if selected_thread:
    st.write("### Chat History")
    for message in st.session_state["threads"][selected_thread]:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")
