import streamlit as st
from openai import OpenAI
from utils import client  # import client directly from utils

# Set Streamlit page configuration
st.set_page_config(page_title="Video Course Assistant", layout='wide')

# Get assistant ID from secrets
ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]

# Helper function to initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

# Initialize session state
init_session_state()

# UI layout
st.title("Video Course Assistant")

# Header section with Video ID, Language, and Session ID
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    video_id = st.text_input("Video ID", placeholder="Enter Video ID", value="312", label_visibility="collapsed")
    st.write(f"**VIDEO ID**: {video_id}")

with col2:
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"], label_visibility="collapsed")
    st.write(f"**LANGUAGE**: {language}")

with col3:
    session_id = st.text_input("Session ID", placeholder="Session ID", value="12", label_visibility="collapsed")
    st.write(f"**Session ID**: {session_id}")

# Functionality buttons and refresh icon in a row
button_col1, button_col2, button_col3, refresh_col = st.columns([1, 1, 1, 0.1])
with button_col1:
    if st.button("SUMMARISE"):
        user_input = f"Summarise the content of the video with ID {video_id} in {language}."
    else:
        user_input = None

with button_col2:
    if st.button("QUIZ ME"):
        user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
    else:
        user_input = None

with button_col3:
    if st.button("ASK A QUESTION"):
        user_input = st.text_input("Type your question here:", key="question_input")
    else:
        user_input = None

with refresh_col:
    if st.button("🔄", key="refresh"):
        st.session_state["messages"] = []
        st.write("Chat reset.")

# Chat area for displaying conversation
st.write("### Chat Area")
chat_placeholder = st.empty()
chat_container = chat_placeholder.container()

# Function to send message to assistant
def send_message(prompt):
    # Create a message in the thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )
    
    # Append the user message to the session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    chat_container.write(f"**You:** {prompt}")
    
    # Create a new run
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
    )
    
    # Wait for run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status == 'failed':
            st.error("Run failed. Please try again.")
            return
    
    # Retrieve messages after run completes
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )
    
    # Get the latest assistant message
    for message in messages:
        if message.role == "assistant":
            assistant_response = message.content[0].text.value
            break
    else:
        assistant_response = "No response received"
    
    # Update the conversation in session state
    st.session_state["messages"].append({
        "role": "assistant",
        "content": assistant_response
    })
    
    chat_container.write(f"**Assistant:** {assistant_response}")

# If there's user input, send it to the assistant
if user_input:
    send_message(user_input)

# Display the conversation history
for message in st.session_state["messages"]:
    if message["role"] == "user":
        chat_container.write(f"**You:** {message['content']}")
    else:
        chat_container.write(f"**Assistant:** {message['content']}")
