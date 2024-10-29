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
from utils import client  # or set up the client as per your configuration

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
    if "video_id" not in st.session_state:
        st.session_state["video_id"] = None
    if "language" not in st.session_state:
        st.session_state["language"] = None
    if "chat_mode" not in st.session_state:
        st.session_state["chat_mode"] = False

# Initialize session state
init_session_state()

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
        pass  # Implement if you have specific tool call handling

    @override
    def on_tool_call_done(self, tool_call):
        pass  # Implement if you have specific tool call handling

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

# Function to format annotations
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

# Function to create file links
def create_file_link(file_name, file_id):
    content = client.files.content(file_id)
    content_type = content.response.headers["content-type"]
    b64 = base64.b64encode(content.text.encode(content.encoding)).decode()
    link_tag = f'<a href="data:{content_type};base64,{b64}" download="{file_name}">Download Link</a>'
    return link_tag

# UI layout
st.title("Video Course Assistant")

# Top bar layout with Video ID and Language
col1, col2 = st.columns([1, 1])
with col1:
    video_id = st.text_input("Video ID", placeholder="Enter Video ID", value="503")
with col2:
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"])

# Display session information
st.write(f"**VIDEO ID**: {video_id}")
st.write(f"**LANGUAGE**: {language}")

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
    # Start a new chat session
    if st.session_state.get("current_thread_id") is None or not st.session_state.get("chat_mode", False):
        initial_prompt = f"The user wants to ask questions about video ID {video_id} in {language}."
        create_new_thread(initial_prompt)
        st.session_state["video_id"] = video_id
        st.session_state["language"] = language
        st.session_state["chat_mode"] = True  # Set chat mode to True

if col7.button("Reset"):
    st.session_state["threads"].clear()
    st.session_state["current_thread_id"] = None
    st.session_state["chat_mode"] = False
    st.write("All threads reset.")

# If in chat mode, display the chat interface
if st.session_state.get("chat_mode", False) and st.session_state["current_thread_id"]:
    st.write("### Chat with the Assistant")
    # Display the conversation history
    messages = st.session_state["threads"][st.session_state["current_thread_id"]]
    for message in messages:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

    # Get user input
    user_message = st.text_input("Your message:", key="user_message_input")
    if user_message:
        if user_message.strip().lower() == "quit":
            st.session_state["chat_mode"] = False
            st.write("Chat ended.")
        else:
            # Include the video ID in the prompt
            prompt = f"Question about video ID {st.session_state['video_id']} in {st.session_state['language']}: {user_message}"
            # Send the message
            send_message(st.session_state["current_thread_id"], prompt)
            # Clear the input field
            st.session_state["user_message_input"] = ""

# Else, display the conversation history for the selected thread
else:
    # Dropdown to select active thread
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
