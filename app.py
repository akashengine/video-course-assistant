"""
    This file demonstrates how to use the OpenAI Assistants API with Streamlit.
    Users upload a CSV and the assistant writes an article about the data. For
    this to work, you'll need to:

    1. Install the streamlit and openai packages
    2. Get an OpenAI API key
    3. Set an environment variable called OPENAI_API_KEY with your API key
    4. Create an assistant with Code Interpreter on, and this system message:
    "You are an experienced data journalist. You receive a CSV of data from a
    user. You write code to find interesting patterns in the data. You choose
    the most interesting of these patterns and write a 250-word article about
    them. You write the headline for the article and then the article itself.
    You do not ask for feedback from the user at any point. You independently
    look for trends, independently write the article, and then provide the
    article to the user to review."

    Once you've done that, replace the <assistant_id> in the code below with 
    your own assistant ID. Then run the code with streamlit run <filename.py>.

"""


import os
import time

import openai
import streamlit as st

# Create an OpenAI client with your API key
openai_client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))

# Retrieve the assistant you want to use
assistant = openai_client.beta.assistants.retrieve(
    "asst_FsFGT6vkPNt1ATj1axikkIzT"
)

# Create the title and subheader for the Streamlit page
st.title("Data Journalist")
st.subheader("Upload a CSV and get the story within:")

# Create a file input for the user to upload a CSV
uploaded_file = st.file_uploader(
    "Upload a CSV", type="csv", label_visibility="collapsed"
)

# If the user has uploaded a file, start the assistant process...
if uploaded_file is not None:
    # Create a status indicator to show the user the assistant is working
    with st.status("Starting work...", expanded=False) as status_box:
        # Upload the file to OpenAI
        file = openai_client.files.create(
            file=uploaded_file, purpose="assistants"
        )

        # Create a new thread with a message that has the uploaded file's ID
        thread = openai_client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "Write an article about this data.",
                    "file_ids": [file.id],
                }
            ]
        )

        # Create a run with the new thread
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Check periodically whether the run is done, and update the status
        while run.status != "completed":
            time.sleep(5)
            status_box.update(label=f"{run.status}...", state="running")
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )

        # Once the run is complete, update the status box and show the content
        status_box.update(label="Complete", state="complete", expanded=True)
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread.id
        )
        st.markdown(messages.data[0].content[0].text.value)

        # Delete the uploaded file from OpenAI
        openai_client.files.delete(file.id)
