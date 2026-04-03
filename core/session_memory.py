# core/session_memory.py
from typing import List, Optional

class SessionMemory:
    """单例记忆模型：模拟 TS 中的 agentMemory，负责跨智能体的背景同步"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.memory = "" # 存储长期会话摘要
        return cls._instance

# 创建全局唯一的记忆实例
SESSION_MEMORY = SessionMemory()

def try_session_memory_compact(messages: List[dict]) -> Optional[List[dict]]:
    """如果有可用的长期摘要，且消息过多，则尝试用摘要替换历史对话"""
    if not SESSION_MEMORY.memory or len(messages) < 10:
        return None
    
    # 保留最近 5 条对话，其余历史用摘要折叠
    keep_msgs = messages[-5:]
    summary_block = {
        "role": "user",
        "content": f"【系统历史背景摘要】\n{SESSION_MEMORY.memory}\n请基于此背景继续执行后续任务。"
    }
    return [summary_block] + keep_msgs