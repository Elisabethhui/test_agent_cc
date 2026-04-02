#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grouping 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
from typing import List

def group_by_api_round(messages: List[dict]) -> List[List[dict]]:
    groups = []
    current = []
    last_aid = None
    for msg in messages:
        role = msg.get("role")
        mid = msg.get("id")
        if role == "assistant" and mid != last_aid and current:
            groups.append(current)
            current = [msg]
            last_aid = mid
        else:
            current.append(msg)
        if role == "assistant":
            last_aid = mid
    if current:
        groups.append(current)
    return groups