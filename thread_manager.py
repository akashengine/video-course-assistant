# thread_manager.py

from uuid import uuid4

class ThreadManager:
    def __init__(self, client, assistant_id):
        self.client = client
        self.assistant_id = assistant_id
        self.threads = {}

    def create_thread(self):
        # Create a new thread using the client and save its ID
        thread = self.client.beta.threads.create()
        thread_id = thread["id"]
        self.threads[thread_id] = {"history": []}
        return thread_id

    def get_thread_history(self, thread_id):
        # Retrieve the conversation history for a specific thread
        return self.threads.get(thread_id, {}).get("history", [])

    def add_message_to_thread(self, thread_id, role, content):
        # Append a new message to the thread's history
        if thread_id in self.threads:
            self.threads[thread_id]["history"].append({"role": role, "content": content})

    def reset_thread(self, thread_id):
        # Clear the chat history of a specific thread
        if thread_id in self.threads:
            self.threads[thread_id]["history"] = []
