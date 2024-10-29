import streamlit as st
import openai
import os

# Configure Streamlit page
st.set_page_config(page_title="Video Course Assistant", page_icon="📹", layout="centered")

# Set up OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Define the Assistant ID
ASSISTANT_ID = "asst_FsFGT6vkPNt1ATj1axikkIzT"

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Summarize"

# Top bar with video ID, language, and session ID
st.markdown(
    f"""
    <div style='display: flex; justify-content: space-between; padding: 1rem; background-color: #f0f0f0;'>
        <div>📹 <strong>VIDEO ID:</strong> 312</div>
        <div>🌐 <strong>LANGUAGE:</strong> English</div>
        <div>🆔 <strong>Session ID:</strong> 12</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Tabs for different actions
tab1, tab2, tab3 = st.columns(3)
if tab1.button("Summarize"):
    st.session_state.active_tab = "Summarize"
if tab2.button("Quiz Me"):
    st.session_state.active_tab = "Quiz Me"
if tab3.button("Ask a Question"):
    st.session_state.active_tab = "Ask a Question"

# Input area for user message
st.write(f"**Mode:** {st.session_state.active_tab}")
user_input = st.text_input("Enter your query:", "")

# Function to interact with OpenAI assistant
def communicate_with_assistant(prompt):
    response = None
    try:
        # Send the request to OpenAI Assistant
        response = openai.Assistant.create_run(
            assistant_id=ASSISTANT_ID,
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract the assistant's reply
        assistant_reply = response["choices"][0]["message"]["content"]
        return assistant_reply
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Submit button to send the user's input to OpenAI Assistant
if st.button("Send") and user_input:
    prompt = ""
    
    # Customize prompt based on active tab
    if st.session_state.active_tab == "Summarize":
        prompt = f"Summarize the content of video ID 312 in {st.session_state.language}."
    elif st.session_state.active_tab == "Quiz Me":
        prompt = f"Generate a quiz based on video ID 312 in {st.session_state.language}."
    elif st.session_state.active_tab == "Ask a Question":
        prompt = user_input
    
    # Get the assistant's response
    assistant_response = communicate_with_assistant(prompt)
    if assistant_response:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    else:
        st.error("Failed to get a response from the assistant.")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Assistant:** {message['content']}")

# Refresh button to clear the chat
if st.button("Refresh"):
    st.session_state.messages = []
    st.experimental_rerun()
