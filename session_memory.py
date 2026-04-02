#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
session_memory 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
from typing import List, Optional
from config import CONFIG
from grouping import group_by_api_round

class SessionMemory:
    _instance = None  # 全局唯一单例

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.memory = ""
            cls._instance.last_summarized_id = None
        return cls._instance

# ✅ 全局唯一实例（任何文件导入都是同一个）
SESSION_MEMORY = SessionMemory()

def try_session_memory_compact(messages: List[dict]) -> Optional[List[dict]]:
    if not SESSION_MEMORY.memory:
        return None

    groups = group_by_api_round(messages)
    keep = groups[-CONFIG.MIN_RETAIN_MESSAGES:]
    keep_msgs = [item for sublist in keep for item in sublist]

    summary = {
        "role": "user",
        "content": f"【会话记忆无损压缩】\n{SESSION_MEMORY.memory}",
        "is_compact_summary": True
    }

    return [summary] + keep_msgs