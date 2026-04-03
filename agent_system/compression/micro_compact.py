from agent_system.core.config import CONFIG, CLEARABLE_TOOL_RESULTS
from agent_system.core.utils import is_tool_result

class CacheState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pending_edits = []
        return cls._instance

CACHE_STATE = CacheState()

def micro_compact(messages):
    tool_ids = []
    for m in messages:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") == "tool_use" and b.get("name") in CLEARABLE_TOOL_RESULTS:
                    tool_ids.append(b.get("id"))
    keep = set(tool_ids[-CONFIG.KEEP_RECENT_TOOLS:])
    CACHE_STATE.pending_edits = [t for t in tool_ids if t not in keep]
    return messages