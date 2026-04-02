#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compact_system 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
import asyncio
from typing import List, Callable, Awaitable
from micro_compact import micro_compact
from session_memory import try_session_memory_compact
from grouping import group_by_api_round
from summary_prompt import get_summary_prompt
from post_clean import post_compact_cleanup
from config import CONFIG
from utils import estimate_tokens
from session_memory import SESSION_MEMORY


async def run_full_compact(
    messages: List[dict],
    model_call: Callable[[List[dict]], Awaitable[str]],
    is_main_thread: bool = True
) -> List[dict]:
    messages = micro_compact(messages)
    compacted = try_session_memory_compact(messages)
    if compacted:
        post_compact_cleanup(is_main_thread)
        return compacted

    total = sum(estimate_tokens(m.get("content")) for m in messages)
    if total < CONFIG.MAX_RETAIN_TOKENS:
        return messages

    groups = group_by_api_round(messages)
    keep = groups[-CONFIG.MIN_RETAIN_MESSAGES:]
    keep_msgs = [x for sub in keep for x in sub]
    summarize = [x for sub in groups[:-CONFIG.MIN_RETAIN_MESSAGES] for x in sub]

    summary = await model_call([
        {"role": "system", "content": get_summary_prompt()},
        {"role": "user", "content": f"请总结对话：{summarize}"}
    ])

    new_msgs = [
        {"role": "user", "content": f"【AI 压缩总结】\n{summary}", "is_compact_summary": True},
        *keep_msgs
    ]
    post_compact_cleanup(is_main_thread)
    return new_msgs