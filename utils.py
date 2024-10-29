# utils.py

import openai

def fetch_openai_response(assistant_id, request_type, video_id, language, user_input):
    """
    Sends a request to the OpenAI Assistant and retrieves the response.

    Parameters:
        assistant_id (str): The unique assistant ID provided by OpenAI.
        request_type (str): Type of request (e.g., Summarize, Quiz Me, Ask a Question).
        video_id (str): The video ID to pass along in the prompt.
        language (str): Language preference for the response.
        user_input (str): User's message or question.

    Returns:
        str: The response from the OpenAI Assistant.
    """
    # Format the prompt dynamically based on inputs
    prompt = f"""
    Type of Request: {request_type}
    Video ID: {video_id}
    Language: {language}

    User Message: {user_input}
    """

    # Send request to OpenAI Assistant using the new API method
    response = openai.Assistant.create_run(
        assistant_id=assistant_id,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the assistant's response
    assistant_message = response["choices"][0]["message"]["content"]
    return assistant_message
