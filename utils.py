import streamlit as st
from openai.types.beta.threads.text_delta_block import TextDeltaBlock

class StreamHandler:
    def __init__(self):
        self.response_text = ""

    def handle_event(self, event):
        # Handle text deltas to simulate streaming
        if isinstance(event, TextDeltaBlock) and event.text:
            self.response_text += event.text.value
            st.session_state["messages"][-1]["content"] = self.response_text
            st.experimental_rerun()  # Update UI
