# thread_manager.py

import openai
from uuid import uuid4

class ThreadManager:
    def __init__(self):
        self.threads = {}

    def create_thread(self, assistant_id, initial_message):
        thread_id = str(uuid4())
        thread = openai.Thread.create(
            assistant_id=assistant_id,
            messages=[{"role": "user", "content": initial_message}]
        )
        self.threads[thread_id] = {"thread": thread, "history": [], "files": []}
        return thread_id

    def get_thread(self, thread_id):
        return self.threads.get(thread_id)

    def add_message_to_thread(self, thread_id, message, role="user"):
        thread = self.threads[thread_id]["thread"]
        thread.messages.create(role=role, content=message)
        self.threads[thread_id]["history"].append({"role": role, "content": message})

    def attach_file_to_thread(self, thread_id, file_path):
        message_file = openai.File.create(file=open(file_path, "rb"), purpose="assistants")
        self.threads[thread_id]["files"].append(message_file.id)
        return message_file.id

    def reset_thread(self, thread_id):
        self.threads[thread_id]["history"] = []
