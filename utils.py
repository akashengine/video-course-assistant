# utils.py

import openai
import pandas as pd

def load_video_titles(file_path):
    """
    Loads the video titles from a CSV file.
    """
    video_titles_df = pd.read_csv(file_path)
    return dict(zip(video_titles_df['video_id'], video_titles_df['file_title_english']))

def fetch_openai_response(request_type, video_id, language, message):
    """
    Formats and sends a request to the OpenAI API.
    """
    prompt = f"""
    Type of Request: {request_type}
    Video ID: {video_id}
    Language: {language}
    
    User Message: {message}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()
