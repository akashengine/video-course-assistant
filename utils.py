import openai
import streamlit as st

# Initialize OpenAI client with API key
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Function to check if a prompt triggers the moderation endpoint
def moderation_endpoint(prompt):
    response = client.Moderation.create(input=prompt)
    return response["results"][0]["flagged"]
