import streamlit as st
import time
from utils import client  # Assuming utils.client is configured correctly

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

# Initialize session state
init_session_state()

# Function to create a new thread and add initial message
def create_new_thread(prompt):
    try:
        # Create a new thread with the initial message
        thread = client.beta.threads.create(messages=[{"role": "user", "content": prompt}])
        thread_id = thread.id
        # Store thread and initial message
        st.session_state["threads"][thread_id] = [{"role": "user", "content": prompt}]
        st.session_state["current_thread_id"] = thread_id
        return thread_id
    except Exception as e:
        st.error(f"Error creating thread: {e}")
        return None

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

# Function buttons
col4, col5, col6, col7 = st.columns([1, 1, 1, 1])
if col4.button("Summarise"):
    prompt = f"Summarise the content of the video with ID {video_id} in {language}."
    thread_id = create_new_thread(prompt)
if col5.button("Quiz Me"):
    prompt = f"Create a quiz based on the video with ID {video_id} in {language}."
    thread_id = create_new_thread(prompt)
if col6.button("Ask a Question"):
    question = st.text_input("Type your question here:")
    if question:
        prompt = question
        thread_id = create_new_thread(prompt)
if col7.button("Reset"):
    st.session_state["threads"].clear()
    st.session_state["current_thread_id"] = None
    st.write("Conversation reset.")

# Dropdown to select active thread
thread_ids = list(st.session_state["threads"].keys())
selected_thread = st.selectbox("Select Thread", thread_ids, index=0) if thread_ids else None
st.session_state["current_thread_id"] = selected_thread

# Function to send message to the assistant
def send_message(thread_id, prompt):
    try:
        # Send message to the assistant in the specified thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )
        
        # Create a new run and wait for completion
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Polling loop to wait for run completion
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                st.error("Run failed. Please try again.")
                return
            time.sleep(1)  # Adding a small delay to avoid rapid polling

        # Retrieve messages after run completes
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        # Get the latest assistant message
        assistant_response = next((message.content[0].text.value for message in messages if message.role == "assistant"), "No response received")
        st.session_state["threads"][thread_id].append({"role": "assistant", "content": assistant_response})
        st.write(f"**Assistant:** {assistant_response}")
    except Exception as e:
        st.error(f"Error sending message: {e}")

# Display the conversation history for the selected thread
if selected_thread:
    st.write("### Chat History")
    for message in st.session_state["threads"][selected_thread]:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")
