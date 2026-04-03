import json
import math
from datetime import datetime

def estimate_tokens(text):
    if not text:
        return 0
    if isinstance(text, (list, dict)):
        text = json.dumps(text, ensure_ascii=False)
    return math.ceil(len(text) / 3.5)

def get_minutes_since(iso_ts):
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return (datetime.utcnow() - dt).total_seconds() / 60
    except:
        return 0

def is_tool_result(block):
    return block.get("type") == "tool_result"

def is_tool_use(block):
    return block.get("type") == "tool_use"