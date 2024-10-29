import streamlit as st
from openai import OpenAI
from utils import StreamHandler

# Set Streamlit page config
st.set_page_config(page_title="Video Course Assistant", layout='wide')

# Initialize OpenAI client with API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
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

    # Display user message in chat
    st.write(f"**You:** {prompt}")

    # Add a placeholder for the assistant response
    st.session_state["messages"].append({"role": "assistant", "content": ""})

    # Create a StreamHandler instance
    handler = StreamHandler()

    # Run the assistant and stream the response, passing only the handler
    with client.beta.threads.runs.stream(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
        event_handler=handler,
        temperature=1.0
    ) as stream:
        for event in stream:
            print("Processing event in stream...")  # Debugging
            handler.handle_event(event)  # Process each event as it comes in


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
