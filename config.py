#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config 模块
自动生成的空文件，可根据业务逻辑实现功能
"""

from dataclasses import dataclass

@dataclass
class CompactConfig:
    MIN_RETAIN_TOKENS: int = 8000
    MIN_RETAIN_MESSAGES: int = 5
    MAX_RETAIN_TOKENS: int = 32000
    TIME_GAP_MINUTES: int = 60
    KEEP_RECENT_TOOLS: int = 5
    CLEARED_MESSAGE: str = "[Old tool result cleared]"
    CACHE_EDIT_SUPPORT: bool = True

CONFIG = CompactConfig()

CLEARABLE_TOOL_RESULTS = {
    "file_read", "shell", "bash", "grep", "glob",
    "web_search", "web_fetch"
}

CLEARABLE_TOOL_USES = {
    "file_edit", "file_write", "notebook_edit"
}