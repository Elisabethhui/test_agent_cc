#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
import json
import math
from datetime import datetime

def estimate_tokens(text: str | list | dict) -> int:
    if not text:
        return 0
    if isinstance(text, (list, dict)):
        text = json.dumps(text, ensure_ascii=False)
    return math.ceil(len(text) / 3.5)

def get_minutes_since(iso_ts: str) -> float:
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return (datetime.utcnow() - dt).total_seconds() / 60
    except:
        return 0

def is_tool_result(block: dict) -> bool:
    return block.get("type") == "tool_result"

def is_tool_use(block: dict) -> bool:
    return block.get("type") == "tool_use"