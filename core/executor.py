# core/executor.py
from typing import List, Optional, Any
from agents import get_agent_by_type
from .compact_system import run_full_compact
from .session_memory import SESSION_MEMORY
from olmx_client import model_call

class AgentExecutor:
    """
    智能体执行引擎：模拟 TypeScript 中的 runAgent.ts
    负责：环境感知、权限校验、压缩调度、API 执行
    """
    def __init__(self, agent_type: str):
        self.agent_def = get_agent_by_type(agent_type)
        self.messages: List[dict] = []

    async def execute(self, user_query: str, extra_context: Any = None):
        print(f"🔄 [Agent: {self.agent_def.agent_type}] 正在执行指令...")
        
        # 1. 动态构造并刷新 System Prompt
        sys_prompt = self.agent_def.get_system_prompt(extra_context)
        
        # 2. 注入长期持久化记忆 (如有)
        if SESSION_MEMORY.memory:
            sys_prompt += f"\n\n[全局记忆]\n{SESSION_MEMORY.memory}"
            
        # 在发送前，确保 system 消息始终在头部
        self.messages = [m for m in self.messages if m["role"] != "system"]
        self.messages.insert(0, {"role": "system", "content": sys_prompt})
        self.messages.append({"role": "user", "content": user_query})

        # 3. 在 API 请求前执行上下文治理 (压缩系统)
        self.messages = await run_full_compact(self.messages, model_call)

        # 4. 执行推理并获取返回
        response_text = await model_call(self.messages)
        
        # 记录 Assistant 的回复到内存
        self.messages.append({"role": "assistant", "content": response_text})
        return response_text