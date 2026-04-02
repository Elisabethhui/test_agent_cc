#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
micro_compact 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
from typing import List
from config import CONFIG, CLEARABLE_TOOL_RESULTS
from utils import estimate_tokens, get_minutes_since, is_tool_result

class CacheEditState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pending_edits = []
            cls._instance.pinned = []
        return cls._instance

# ✅ 单例
CACHE_STATE = CacheEditState()

def time_based_micro_compact(messages: List[dict]) -> List[dict]:
    if not messages:
        return messages

    last = messages[-1]
    ts = last.get("timestamp")
    if ts and get_minutes_since(ts) >= CONFIG.TIME_GAP_MINUTES:
        tool_ids = []
        for m in messages:
            if m.get("role") == "user" and isinstance(m.get("content"), list):
                for b in m["content"]:
                    if is_tool_result(b) and b.get("name") in CLEARABLE_TOOL_RESULTS:
                        tool_ids.append(b.get("tool_use_id"))
        keep = set(tool_ids[-CONFIG.KEEP_RECENT_TOOLS:])
        new_msgs = []
        for m in messages:
            if m.get("role") != "user" or not isinstance(m.get("content"), list):
                new_msgs.append(m)
                continue
            nc = []
            for b in m["content"]:
                if is_tool_result(b) and b.get("tool_use_id") not in keep:
                    nc.append({"type": "tool_result", "content": CONFIG.CLEARED_MESSAGE})
                else:
                    nc.append(b)
            new_msgs.append({**m, "content": nc})
        return new_msgs
    return messages

def cache_edit_clean(messages: List[dict]) -> List[dict]:
    tool_ids = []
    for m in messages:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") == "tool_use" and b.get("name") in CLEARABLE_TOOL_RESULTS:
                    tool_ids.append(b.get("id"))
    keep = set(tool_ids[-CONFIG.KEEP_RECENT_TOOLS:])
    CACHE_STATE.pending_edits = [t for t in tool_ids if t not in keep]
    return messages

def micro_compact(messages: List[dict]) -> List[dict]:
    messages = time_based_micro_compact(messages)
    messages = cache_edit_clean(messages)
    return messages