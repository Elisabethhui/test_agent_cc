from dataclasses import dataclass
from typing import Dict, List
import time

@dataclass
class AgentMemory:
    session_id: str
    agent_type: str = "default"
    project_info: str = ""
    tech_stack: List[str] = None
    task: str = ""
    progress: str = ""
    compressed_history: str = ""
    last_compressed_at: float = 0.0

    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []

class AgentMemoryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.memories: Dict[str, AgentMemory] = {}
        return cls._instance

    def get(self, session_id: str, agent_type="default"):
        if session_id not in self.memories:
            self.memories[session_id] = AgentMemory(
                session_id=session_id, agent_type=agent_type
            )
        return self.memories[session_id]

    def update_compressed(self, session_id: str, summary: str):
        mem = self.get(session_id)
        mem.compressed_history = summary
        mem.last_compressed_at = time.time()

AGENT_MEMORY = AgentMemoryManager()