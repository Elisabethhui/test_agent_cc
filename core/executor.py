# core/executor.py
import time
from core.micro_compact import micro_compact_logic
from core.compact_system import run_auto_compact
from core.session_memory import session_mem
from utils import is_context_stale

class AgentExecutor:
    def __init__(self, agent_instance, client):
        self.agent = agent_instance
        self.client = client
        self.messages = []
        self.last_interaction = time.time()

    def _assemble_prompt_layers(self):
        """
        修复此处：确保能拿到 system_prompt
        """
        # 容错处理：优先读取属性，如果没有则尝试调用方法
        if hasattr(self.agent, 'system_prompt'):
            role_layer = self.agent.system_prompt
        elif hasattr(self.agent, 'get_system_prompt'):
            role_layer = self.agent.get_system_prompt()
        else:
            role_layer = "You are a helpful AI assistant."

        memory_layer = session_mem.get_context_block()
        constraint_layer = f"=== CONSTRAINTS ===\n- 禁用工具: {getattr(self.agent, 'disallowed_tools', [])}"
        
        return f"{role_layer}\n\n{memory_layer}\n\n{constraint_layer}"

    async def run_turn(self, user_query: str):
        # 1. 微压缩 (物理清理)
        self.messages = micro_compact_logic(self.messages)
        
        # 2. 全量压缩 (逻辑总结)
        self.messages = await run_auto_compact(self.messages, self.client)
        
        # 3. 构造分层提示词
        sys_p = self._assemble_prompt_layers()
        
        # 4. 模型推理
        payload = [{"role": "system", "content": sys_p}] + self.messages + [{"role": "user", "content": user_query}]
        response = await self.client.generate(payload)
        
        # 5. 更新状态
        self.messages.append({"role": "user", "content": user_query})
        self.messages.append({"role": "assistant", "content": response})
        self.last_interaction = time.time()
        
        return response