# utils.py
import json
import math
from datetime import datetime, timezone
# utils.py
import time
# utils.py
from config import CONFIG
def estimate_tokens(text: str | list | dict) -> int:
    """
    估算内容的 Token 数量 (工业级粗略计算：字符数 / 3.5)
    """
    if not text:
        return 0
    if isinstance(text, (list, dict)):
        text = json.dumps(text, ensure_ascii=False)
    return math.ceil(len(text) / 3.5)

def get_minutes_since(iso_ts: str) -> float:
    """计算自 ISO 时间戳到现在经过的分钟数，用于微压缩判断"""
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds() / 60
    except:
        return 0

def is_tool_result(block: dict) -> bool:
    """判断内容块是否为工具执行的结果"""
    return block.get("type") == "tool_result"

def is_tool_use(block: dict) -> bool:
    """判断内容块是否为模型发出的工具调用指令"""
    return block.get("type") == "tool_use"


def count_tokens(text: str) -> int:
    """
    估算文本的 Token 数量。
    参考 Claude Code 中的估算逻辑，这里使用字符数除以 4。
    """
    if not text:
        return 0
    return len(str(text)) // 4

def is_context_stale(last_ts: float) -> bool:
    """
    判断当前对话是否超过了设定的时间窗口 (30分钟)。
    用于触发基于时间的自动微压缩。
    """
    elapsed_mins = (time.time() - last_ts) / 60
    return elapsed_mins > CONFIG.TIME_GAP_THRESHOLD_MINS