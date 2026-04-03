# core/session_memory.py
import json
import os

class SessionMemory:
    """复刻 agentMemory.ts 的三层作用域管理"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionMemory, cls).__new__(cls)
            cls._instance.memory = {
                "user": {},    # 跨项目习惯
                "project": {}, # 团队规范
                "local": {}    # 本次任务临时状态
            }
        return cls._instance

    def save_to_scope(self, scope: str, key: str, value: str):
        if scope in self.memory:
            self.memory[scope][key] = value
            # 模拟持久化到磁盘
            print(f"[Memory] Saved to {scope}: {key}")

    def get_full_context_string(self) -> str:
        """用于 Prompt Layering 的记忆层注入"""
        context = "=== DYNAMIC MEMORY ===\n"
        for scope, items in self.memory.items():
            if items:
                context += f"[{scope.upper()} SCOPE]: {json.dumps(items, ensure_ascii=False)}\n"
        return context

session_mem = SessionMemory()