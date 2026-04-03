from dataclasses import dataclass

@dataclass
class AgentContext:
    session_id: str
    is_main_thread: bool
    agent_type: str

class AgentContextManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create(self, session_id: str, agent_type="default"):
        is_main = (
            session_id.startswith("repl_main_")
            or session_id == "sdk"
            or not session_id.startswith("agent:")
        )
        return AgentContext(
            session_id=session_id,
            is_main_thread=is_main,
            agent_type=agent_type
        )

AGENT_CONTEXT = AgentContextManager()