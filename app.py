import streamlit as st
import time
from utils import client  # Assuming utils.client is configured correctly

# Set Streamlit page configuration
st.set_page_config(page_title="Video Course Assistant", layout="wide")

# Constants
ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]

# Helper function to initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()  # Start a new thread initially
        st.session_state.thread_id = thread.id

# Initialize session state
init_session_state()

# Function to reset the thread and start a new conversation
def reset_thread():
    thread = client.beta.threads.create()  # Create a new thread
    st.session_state.thread_id = thread.id
    st.session_state["messages"] = []  # Clear message history
    st.write("New conversation started.")

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
if col5.button("Quiz Me"):
    user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
if col6.button("Ask a Question"):
    question = st.text_input("Type your question here:")
    if question:
        user_input = question
if col7.button("Reset"):
    reset_thread()  # Reset the thread and start a new conversation

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
    st.write(f"**You:** {prompt}")
    
    # Create a new run
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
    )
    
    # Wait for the run to complete, with a small delay to prevent excessive polling
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
        time.sleep(1)  # Small delay to avoid rapid polling
    
    # Retrieve messages after the run completes
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    
    # Get the latest assistant message
    assistant_response = next((msg.content[0].text.value for msg in messages if msg.role == "assistant"), "No response received")
    
    # Update the conversation in session state
    st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
    st.write(f"**Assistant:** {assistant_response}")

# If there's user input, send it to the assistant
if user_input:
    send_message(user_input)

# Display the conversation history
st.write("### Chat History")
for message in st.session_state["messages"]:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Assistant:** {message['content']}")
