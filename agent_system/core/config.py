from dataclasses import dataclass

@dataclass
class CompactConfig:
    MIN_RETAIN_TOKENS: int = 8000
    MIN_RETAIN_MESSAGES: int = 5
    MAX_RETAIN_TOKENS: int = 15000
    TIME_GAP_MINUTES: int = 60
    KEEP_RECENT_TOOLS: int = 5
    CLEARED_MESSAGE: str = "[Old tool result cleared]"
    CACHE_EDIT_SUPPORT: bool = True

CONFIG = CompactConfig()

CLEARABLE_TOOL_RESULTS = {
    "file_read", "shell", "bash", "grep", "glob",
    "web_search", "web_fetch"
}