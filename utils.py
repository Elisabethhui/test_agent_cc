# utils.py
import json
import math
from datetime import datetime, timezone
# utils.py
import time
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
    # 模拟简单计数，实际可使用 tiktoken 或 model-specific tokenizer
    return len(text) // 4

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_stale(last_interaction_time: float, threshold_minutes: int) -> bool:
    """模拟 microCompact.ts 中的时间感知逻辑"""
    elapsed = (time.time() - last_interaction_time) / 60
    return elapsed > threshold_minutes