# app.py

import streamlit as st
from openai import OpenAI
from thread_manager import ThreadManager

# Initialize the OpenAI client with the API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Define the assistant ID
ASSISTANT_ID = "asst_FsFGT6vkPNt1ATj1axikkIzT"

# Initialize the ThreadManager with the assistant ID and client
thread_manager = ThreadManager(client, ASSISTANT_ID)

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
if st.session_state.threads:
    selected_thread_id = st.sidebar.selectbox("Select a Thread", list(st.session_state.threads.keys()), format_func=lambda x: st.session_state.threads[x])
    if selected_thread_id:
        st.session_state.active_thread = selected_thread_id

    # Display the name of the active thread
    st.write(f"**Active Thread**: {st.session_state.threads[st.session_state.active_thread]}")

    # Sidebar inputs for selecting Video ID, Language, and Request Type
    video_id = st.sidebar.text_input("Video ID", value="312")  # Default video ID for testing
    language = st.sidebar.selectbox("Select Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam"])
    request_type = st.sidebar.radio("Type of Request", ["Summarize", "Quiz Me", "Ask a Question"])

    # Chat Interface
    st.markdown("### Chat Interface")
    user_input = st.text_input("Your question/message:")

    # Send button
    if st.button("Send"):
        if user_input and st.session_state.active_thread:
            # Format the prompt with the selected options
            prompt = f"""
            Type of Request: {request_type}
            Video ID: {video_id}
            Language: {language}

            User Message: {user_input}
            """

            # Create a message in the active thread
            client.beta.threads.messages.create(
                thread_id=st.session_state.active_thread,
                role="user",
                content=prompt
            )

            # Run the assistant on the thread and get the response
            response = client.beta.threads.runs.create(
                thread_id=st.session_state.active_thread,
                assistant_id=ASSISTANT_ID,
            )

            # Extract the assistant's response
            assistant_message = response["messages"][-1]["content"]

            # Update the chat history in the thread manager
            thread_manager.add_message_to_thread(st.session_state.active_thread, "user", user_input)
            thread_manager.add_message_to_thread(st.session_state.active_thread, "assistant", assistant_message)

    # Display chat history for the active thread
    chat_history = thread_manager.get_thread_history(st.session_state.active_thread)
    for entry in chat_history:
        if entry["role"] == "user":
            st.write(f"You: {entry['content']}")
        else:
            st.write(f"Assistant: {entry['content']}")

    # Reset button to clear the chat history for the active thread
    if st.button("Reset Chat"):
        thread_manager.reset_thread(st.session_state.active_thread)
