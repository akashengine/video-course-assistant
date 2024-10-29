import os
import time
import openai
import streamlit as st

# Set up OpenAI client with your API key
openai_client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))

# Retrieve the assistant using the provided assistant ID
assistant = openai_client.beta.assistants.retrieve("asst_FsFGT6vkPNt1ATj1axikkIzT")

# Create the Streamlit app layout
st.title("Video Course Assistant")

# Input for Video ID
video_id = st.text_input("Video ID", placeholder="Enter Video ID", value="312")

# Dropdown for Language selection
language = st.selectbox(
    "Language",
    ["English", "Hindi", "Telugu", "Tamil", "Malayalam", "Kannada", "Gujarati", "Marathi", "Bengali", "Punjabi"]
)

# Initialize session state to keep track of chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display current session information
st.write(f"**Video ID**: {video_id}")
st.write(f"**Language**: {language}")

# Add buttons for different functionalities
col1, col2, col3, col4 = st.columns([1, 1, 1, 0.2])
if col1.button("SUMMARISE"):
    user_input = "Summarise the content of the video."
elif col2.button("QUIZ ME"):
    user_input = "Create a quiz based on the video content."
elif col3.button("ASK A QUESTION"):
    user_input = st.text_input("Ask a question about the video:", "")
else:
    user_input = ""

# Function to interact with the assistant
def get_assistant_response(prompt):
    # Create a new thread for each new conversation
    thread = openai_client.beta.threads.create(
        messages=[{"role": "user", "content": prompt}]
    )

    # Run the assistant on the created thread
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Poll for the completion status
    while run.status != "completed":
        time.sleep(5)
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )

    # Retrieve and return the assistant's response
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    assistant_reply = messages.data[0].content[0].text.value
    return assistant_reply

# When the user submits a message
if (user_input and user_input != ""):
    # Display the user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get the assistant response
    assistant_response = get_assistant_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Display the conversation history
st.write("### Chat History")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Assistant:** {message['content']}")
