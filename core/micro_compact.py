# core/micro_compact.py
from typing import List
from config import CONFIG, CLEARABLE_TOOL_RESULTS
from utils import is_tool_result

def micro_compact(messages: List[dict]) -> List[dict]:
    """
    微压缩：清理陈旧的、体积庞大的工具执行结果 (如庞大的 ls 或 cat 内容)
    映射 TS 中的 filterUnresolvedToolUses 核心逻辑
    """
    if len(messages) < 8:
        return messages

    new_messages = []
    for m in messages:
        # 仅针对用户角色下的工具返回结果进行内容清洗
        if m.get("role") == "user" and isinstance(m.get("content"), list):
            new_content = []
            for block in m["content"]:
                # 如果是可清理的搜索/读文件结果，将其内容替换为简短占位符
                if is_tool_result(block) and block.get("name") in CLEARABLE_TOOL_RESULTS:
                    new_content.append({
                        "type": "tool_result",
                        "content": CONFIG.CLEARED_MESSAGE,
                        "tool_use_id": block.get("tool_use_id")
                    })
                else:
                    new_content.append(block)
            new_messages.append({**m, "content": new_content})
        else:
            new_messages.append(m)
    return new_messages