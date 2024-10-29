import streamlit as st
from openai import OpenAI
from utils import StreamHandler

# Set up page
st.set_page_config(page_title="Video Course Assistant", layout="wide")

# Retrieve API key and assistant ID from secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id

# Display UI
st.title("Video Course Assistant")
video_id = st.text_input("Video ID", placeholder="Enter Video ID", value="503")
language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"])

# Action based on user input
if st.button("Summarize"):
    user_input = f"Summarize the content of the video with ID {video_id} in {language}."
elif st.button("Quiz Me"):
    user_input = f"Create a quiz based on the video with ID {video_id} in {language}."
elif st.button("Ask a Question"):
    user_input = st.text_input("Type your question here:")
else:
    user_input = None

# Function to send message to assistant
def send_message(prompt):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.write(f"**You:** {prompt}")

    st.session_state["messages"].append({"role": "assistant", "content": ""})
    handler = StreamHandler()

    # Run assistant response stream
    with client.beta.threads.runs.stream(
        thread_id=st.session_state["thread_id"],
        assistant_id=ASSISTANT_ID,
        event_handler=handler,
        temperature=1.0
    ) as stream:
        for event in stream:
            handler.handle_event(event)  # Process each event

# If user input is provided, send message
if user_input:
    send_message(user_input)

# Display conversation history
st.write("### Chat History")
for message in st.session_state["messages"]:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Assistant:** {message['content']}")
