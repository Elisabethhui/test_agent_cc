# core/grouping.py
from typing import List

def group_by_api_round(messages: List[dict]) -> List[List[dict]]:
    """按 Assistant 回复作为界限，对对话进行物理逻辑分组"""
    groups = []
    current_group = []
    for msg in messages:
        current_group.append(msg)
        if msg.get("role") == "assistant":
            groups.append(current_group)
            current_group = []
    if current_group:
        groups.append(current_group)
    return groups