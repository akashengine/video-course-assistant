import streamlit as st

def init_session_state(client):
    """Initialize session state for the assistant app."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "thread_id" not in st.session_state:
        # Create a new thread and store the ID in session state
        thread = client.beta.threads.create()
        st.session_state["thread_id"] = thread.id
