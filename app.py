import os
import base64
import re
import json
import time

import streamlit as st
st.set_page_config(page_title="Video Course Assistant", layout="wide")

from openai import AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv

# Assuming utils.client is configured correctly
from utils import client  # or set up the client as per your configuration

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
        pass  # Implement if needed

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
        pass  # Implement if needed

    @override
    def on_tool_call_done(self, tool_call):
        pass  # Implement if needed

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
    text_value = text.value
    for index, annotation in enumerate(text.annotations):
        text_value = text_value.replace(annotation.text, f" [{index}]")

        if hasattr(annotation, "file_path"):
            file_path = annotation.file_path
            link_tag = create_file_link(
                annotation.text.split("/")[-1],
                file_path.file_id,
            )
            text_value = re.sub(r"\[(.*?)\]\s*\(\s*(.*?)\s*\)", link_tag, text_value)

    return text_value

# Function to create file links
def create_file_link(file_name, file_id):
    content = client.files.content(file_id)
    content_type = content.response.headers["content-type"]
    b64 = base64.b64encode(content.text.encode(content.encoding)).decode()
    link_tag = f'<a href="data:{content_type};base64,{b64}" download="{file_name}">Download Link</a>'
    return link_tag

# Updated video_data list
video_data = [
    # Hindi Literature Main Classes
    # Hindi Literature Main Classes
    "498: Hindi Lit Class 01",
    "499: Hindi Lit Class 02",
    "503: Hindi Lit Class 03",
    "500: Hindi Lit Class 04",
    "501: Hindi Lit Class 05",
    "502: Hindi Lit Class 06",
    "505: Hindi Lit Class 07",
    "506: Hindi Lit Class 08",
    "504: Hindi Lit Class 09",
    "507: Hindi Lit Class 10",
    "509: Hindi Lit Class 11",
    "508: Hindi Lit Class 12",
    "510: Hindi Lit Class 13",
    "511: Hindi Lit Class 14",
    "512: Hindi Lit Class 15",
    "513: Hindi Lit Class 16",
    "516: Hindi Lit Class 17",
    "514: Hindi Lit Class 18",
    "515: Hindi Lit Class 19",
    "517: Hindi Lit Class 20",
    "518: Hindi Lit Class 21",
    "519: Hindi Lit Class 22",
    "522: Hindi Lit Class 23",
    "520: Hindi Lit Class 24",
    "521: Hindi Lit Class 25",
    "525: Hindi Lit Class 26",
    "523: Hindi Lit Class 27",
    "524: Hindi Lit Class 28",
    "526: Hindi Lit Class 29",
    "527: Hindi Lit Class 30",
    "529: Hindi Lit Class 31",
    "528: Hindi Lit Class 32",
    "530: Hindi Lit Class 33",
    "531: Hindi Lit Class 34",
    "532: Hindi Lit Class 35",
    "533: Hindi Lit Class 36",
    "544: Hindi Lit Class 37",
    "545: Hindi Lit Class 38",
    "546: Hindi Lit Class 39",
    "548: Hindi Lit Class 40",
    "547: Hindi Lit Class 41",
    "551: Hindi Lit Class 42",
    "549: Hindi Lit Class 43",
    "550: Hindi Lit Class 44",
    "780: Hindi Lit Class 45",
    "556: Hindi Lit Class 46",
    "552: Hindi Lit Class 47",
    "553: Hindi Lit Class 48",
    "554: Hindi Lit Class 49",
    "555: Hindi Lit Class 50",
    "557: Hindi Lit Class 51",
    "558: Hindi Lit Class 52",
    "559: Hindi Lit Class 53",
    "560: Hindi Lit Class 54",
    "563: Hindi Lit Class 55",
    "565: Hindi Lit Class 56",
    "566: Hindi Lit Class 57",
    "567: Hindi Lit Class 58",
    "570: Hindi Lit Class 59",
    "568: Hindi Lit Class 60",
    "569: Hindi Lit Class 61",
    "572: Hindi Lit Class 62",
    "573: Hindi Lit Class 63",
    "561: Hindi Lit Class 64",
    "562: Hindi Lit Class 65",
    "564: Hindi Lit Class 66",
    "574: Hindi Lit Class 67",
    "575: Hindi Lit Class 68",
    "571: Hindi Lit Class 69",
    "580: Hindi Lit Class 70",
    "579: Hindi Lit Class 71",
    "576: Hindi Lit Class 72",
    "581: Hindi Lit Class 73",
    "578: Hindi Lit Class 74",
    "577: Hindi Lit Class 75",
    "582: Hindi Lit Class 76",
    "583: Hindi Lit Class 77",
    "585: Hindi Lit Class 78",
    "584: Hindi Lit Class 79",
    "586: Hindi Lit Class 80",
    "587: Hindi Lit Class 81",
    "591: Hindi Lit Class 82",
    "589: Hindi Lit Class 83",
    "590: Hindi Lit Class 84",
    "588: Hindi Lit Class 85",
    "592: Hindi Lit Class 86",
    "593: Hindi Lit Class 87",
    "596: Hindi Lit Class 88",
    "594: Hindi Lit Class 89",
    "595: Hindi Lit Class 90",
    "597: Hindi Lit Class 91",
    "598: Hindi Lit Class 92",
    "599: Hindi Lit Class 93",
    "602: Hindi Lit Class 94",
    "606: Hindi Lit Class 95",
    "603: Hindi Lit Class 96",
    "604: Hindi Lit Class 97",
    "605: Hindi Lit Class 98",
    "607: Hindi Lit Class 99",
    "608: Hindi Lit Class 100",
    "609: Hindi Lit Class 101",
    "610: Hindi Lit Class 102",
    "611: Hindi Lit Class 103",
    "612: Hindi Lit Class 104",
    "613: Hindi Lit Class 105",
    "614: Hindi Lit Class 106",
    "615: Hindi Lit Class 107",
    "616: Hindi Lit Class 108",
    "617: Hindi Lit Class 109",
    "618: Hindi Lit Class 110",
    "621: Hindi Lit Class 111",
    "623: Hindi Lit Class 112",
    "622: Hindi Lit Class 113",
    "624: Hindi Lit Class 114",
    "625: Hindi Lit Class 115",
    "656: Hindi Lit Class 116",
    "657: Hindi Lit Class 117",
    "658: Hindi Lit Class 118",
    "662: Hindi Lit Class 119",
    "663: Hindi Lit Class 120",
    "639: Hindi Lit Class 121",
    "640: Hindi Lit Class 122",
    "641: Hindi Lit Class 123",
    "642: Hindi Lit Class 124",
    "643: Hindi Lit Class 125",
    "644: Hindi Lit Class 126",
    "645: Hindi Lit Class 127",
    "646: Hindi Lit Class 128",
    "647: Hindi Lit Class 129",
    "648: Hindi Lit Class 130",
    "649: Hindi Lit Class 131",
    "650: Hindi Lit Class 132",
    "695: Hindi Lit Class 133",
    "696: Hindi Lit Class 134",
    "697: Hindi Lit Class 135",
    "628: Hindi Lit Class 136",
    "629: Hindi Lit Class 137",
    "630: Hindi Lit Class 138",
    "653: Hindi Lit Class 139",
    "631: Hindi Lit Class 140",
    "632: Hindi Lit Class 141",
    "634: Hindi Lit Class 142",
    "633: Hindi Lit Class 143",
    "661: Hindi Lit Class 144",
    "660: Hindi Lit Class 145",
    "659: Hindi Lit Class 146",
    "635: Hindi Lit Class 147",
    "638: Hindi Lit Class 148",
    "636: Hindi Lit Class 149",
    "637: Hindi Lit Class 150",
    "664: Hindi Lit Class 151",
    "665: Hindi Lit Class 152",
    "691: Hindi Lit Class 153",
    "694: Hindi Lit Class 154",
    "693: Hindi Lit Class 155",
    "692: Hindi Lit Class 156",
    "690: Hindi Lit Class 157",
    "710: Hindi Lit Class 158",
    "711: Hindi Lit Class 159",
    "712: Hindi Lit Class 160",
    "713: Hindi Lit Class 161",
    "715: Hindi Lit Class 162",
    "714: Hindi Lit Class 163",
    "717: Hindi Lit Class 164",
    "716: Hindi Lit Class 165",
    "719: Hindi Lit Class 166",
    "720: Hindi Lit Class 167",
    "722: Hindi Lit Class 168",
    "721: Hindi Lit Class 169",
    
    # BPSC Classes
    "1184: Hindi Lit BPSC Class 01",
    "1185: Hindi Lit BPSC Class 02",
    "1186: Hindi Lit BPSC Class 03",
    "1187: Hindi Lit BPSC Class 04",
    "1188: Hindi Lit BPSC Class 05",
    "1189: Hindi Lit BPSC Class 06",
    "1190: Hindi Lit BPSC Class 07",
    "1194: Hindi Lit BPSC Class 08",
    "1204: Hindi Lit BPSC Class 09",
    "1212: Hindi Lit BPSC Class 10"
]

# UI layout
st.title("Video Course Assistant")

# Top bar layout with Video ID and Language
col1, col2 = st.columns([1, 1])
with col1:
    # Use video_data instead of video_ids
    selected_video = st.selectbox("Video ID", video_data, index=video_data.index("503: Hindi Lit Class 03"))
    # Extract the video ID from the selected item
    video_id = selected_video.split(":")[0].strip()
with col2:
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"])

# Display session information
st.write(f"**VIDEO ID**: {video_id}")
st.write(f"**LANGUAGE**: {language}")

# Embed the video player
# Generate the iframe URL based on the selected video ID
iframe_url = f"https://console.drishtiias.com/auth_panel/file_manager/library/video_player_tNv50qIN68G1zQpGG1wdXMUcnTCcrER8So/{video_id}"

# Display the video using an iframe
st.markdown(
    f"""
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
        <iframe src="{iframe_url}" style="position: absolute; top:0; left: 0; width: 100%; height: 100%;" frameborder="0" allowfullscreen></iframe>
    </div>
    """,
    unsafe_allow_html=True,
)

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

    # Use a form to get user input and submit
    with st.form(key='chat_form', clear_on_submit=True):
        user_message = st.text_input("Your message: Or Enter Quit", key="user_message_input")
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_message:
            if user_message.strip().lower() == "quit":
                st.session_state["chat_mode"] = False
                st.write("Chat ended.")
            else:
                # Include the video ID in the prompt
                prompt = f"Question about video ID {st.session_state['video_id']} in {st.session_state['language']}: {user_message}"
                # Send the message
                send_message(st.session_state["current_thread_id"], prompt)
                # No need to clear the input field manually; it's handled by clear_on_submit

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
