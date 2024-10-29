import streamlit as st
from openai import OpenAI
from utils import moderation_endpoint

# Set Streamlit page config
st.set_page_config(page_title="Video Course Assistant", layout='wide')

# Get secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]

# Initialize OpenAI client and retrieve the assistant
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

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
user_input = ""
if st.button("Summarise"):
    user_input = f"Summarise the content of the video with ID {video_id} in {language}."
elif st.button("Quiz Me"):
    user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
elif st.button("Ask a Question"):
    user_input = st.text_input("Type your question here:")

# Function to send message to assistant
def send_message(prompt):
    # Append the user message to the session state for tracking
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display user message in chat
    st.write(f"**You:** {prompt}")

    # Add a placeholder for the assistant response
    st.session_state["messages"].append({"role": "assistant", "content": ""})

    # Create a new run
    response = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
    )

    # Fetch the run result
    run_result = client.beta.threads.runs.retrieve(
        thread_id=st.session_state.thread_id,
        run_id=response.id
    )

    # Assuming the response content can be accessed directly
    assistant_response = run_result.get("content", "No response received")

    # Update the session state with the assistant's response
    st.session_state["messages"][-1]["content"] = assistant_response
    st.write(f"**Assistant:** {assistant_response}")
