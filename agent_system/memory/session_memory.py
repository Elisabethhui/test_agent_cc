from typing import Dict
from dataclasses import dataclass
import time

@dataclass
class SessionMemory:
    session_id: str
    content: str = ""
    last_summarized_msg_id: str = None

class SessionMemoryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.sessions: Dict[str, SessionMemory] = {}
        return cls._instance

    def get(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id=session_id)
        return self.sessions[session_id]

    def update(self, session_id: str, content: str):
        mem = self.get(session_id)
        mem.content = content

SESSION_MEMORY = SessionMemoryManager()