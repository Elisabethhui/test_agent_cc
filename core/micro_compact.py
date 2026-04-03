# core/micro_compact.py
from config import TOOLS_TO_DEHYDRATE, MICRO_COMPACT_THRESHOLD

def dehydration_strategy(messages: list) -> list:
    """
    物理脱水策略 (复刻 microCompact.ts):
    对过早且过大的工具执行结果进行物理删除，仅保留摘要。
    """
    processed = []
    # 倒数 3 轮之后的消息才允许脱水，保证当前的上下文新鲜度
    protected_zone = 6 
    
    for i, msg in enumerate(messages):
        if i < len(messages) - protected_zone:
            if msg.get("role") == "tool" and msg.get("name") in TOOLS_TO_DEHYDRATE:
                content = str(msg.get("content", ""))
                if len(content) > MICRO_COMPACT_THRESHOLD:
                    # 执行物理剔除
                    msg["content"] = f"[CONTENT DEHYDRATED: Output was too long ({len(content)} chars)]"
                    msg["was_compacted"] = True
        processed.append(msg)
    return processed