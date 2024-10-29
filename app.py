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
video_id = st.text_input("Video ID", placeholder="Enter Video ID", value="503")
language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"])

# Display session information
st.write(f"**Video ID**: {video_id}")
st.write(f"**Language**: {language}")

# Buttons for different functionalities
if st.button("Summarise"):
    user_input = f"Summarise the content of the video with ID {video_id} in {language}."
elif st.button("Quiz Me"):
    user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
elif st.button("Ask a Question"):
    user_input = st.text_input("Type your question here:")
else:
    user_input = None

# Function to send message to assistant
def send_message(prompt):
    # Append the user message to the session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.write(f"**You:** {prompt}")

    # Add a placeholder for the assistant response
    st.session_state["messages"].append({"role": "assistant", "content": ""})

    # Create a new run and get a response
    response = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
    )

    # Retrieve the result of the run
    run_result = client.beta.threads.runs.retrieve(
        thread_id=st.session_state.thread_id, run_id=response.id
    )

    # Access the assistant's response text content directly
    if run_result.content and len(run_result.content) > 0:
        assistant_response = run_result.content[0].text.value
    else:
        assistant_response = "No response received"

    # Update the assistant response in session state
    st.session_state["messages"][-1]["content"] = assistant_response
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
