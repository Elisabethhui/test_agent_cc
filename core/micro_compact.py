# core/micro_compact.py
from config import CONFIG, CLEARABLE_TOOLS

def micro_compact_logic(messages: list) -> list:
    """
    物理脱水 (Micro-Compaction) 策略：
    1. 扫描消息流。
    2. 识别陈旧的工具执行结果（属于 CLEARABLE_TOOLS 且不再是最近 2 次的结果）。
    3. 物理剔除内容并替换为 Stub 占位符。
    """
    if len(messages) <= CONFIG.MIN_RETAIN_MESSAGES:
        return messages

    # 统计已见到的工具结果数量（从新到旧）
    tool_results_count = 0
    new_messages = []
    
    # 逆向遍历以保留“新鲜”的工具输出
    for msg in reversed(messages):
        is_tool = msg.get("role") == "tool"
        
        if is_tool:
            tool_results_count += 1
            # 如果是需要清理的工具，且已经超出了保留窗口
            if tool_results_count > CONFIG.KEEP_RECENT_TOOLS_COUNT:
                # 某些实现中 name 存在于 msg['name']，某些在 content 标记中
                tool_name = msg.get("name", "")
                if tool_name in CLEARABLE_TOOLS or not tool_name:
                    msg["content"] = CONFIG.CLEARED_STUB
                    msg["was_micro_compacted"] = True
        
        new_messages.append(msg)
    
    return list(reversed(new_messages))

