import base64
import os
import streamlit as st
from openai import OpenAI
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 

# Initialize OpenAI client with API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Custom StreamHandler for streaming
class StreamHandler:
    def __init__(self):
        self.response_text = ""
    
    def handle_event(self, event):
        # Handle streaming text deltas and update assistant's message in real-time
        if isinstance(event, TextDeltaBlock):
            if event.text:
                self.response_text += event.text.value
                st.session_state["messages"][-1]["content"] = self.response_text
                st.experimental_rerun()  # Update the chat UI in real-time

# Function to check if a prompt triggers the moderation endpoint
def moderation_endpoint(prompt):
    response = client.moderations.create(input=prompt)
    return response.results[0].flagged
