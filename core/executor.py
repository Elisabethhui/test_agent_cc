# core/executor.py
import time
from core.micro_compact import dehydration_strategy
from core.compact_system import run_auto_compact
from core.session_memory import session_mem
from utils import get_timestamp

class AgentExecutor:
    """
    对应 AgentTool.tsx 协调器模式
    实现提示词分层 (Prompt Layering) 和 运行循环
    """
    def __init__(self, agent_config, client):
        self.agent_config = agent_config
        self.client = client
        self.messages = []
        self.last_interaction = time.time()

    def _build_layered_prompt(self, user_query: str):
        """
        提示词分层架构:
        1. 静态系统层 (Static)
        2. 环境感知层 (Env)
        3. 动态记忆层 (Memory)
        4. 任务特定层 (Task)
        """
        env_details = f"CWD: {self.agent_config.get('cwd', '/')}\nTime: {get_timestamp()}"
        memory_details = session_mem.get_full_context_string()
        
        system_prompt = f"""
{self.agent_config['system_prompt']}

=== ENVIRONMENT ===
{env_details}

{memory_details}
"""
        return system_prompt

    async def run_turn(self, user_input: str):
        # 1. 微压缩 (物理清理)
        self.messages = dehydration_strategy(self.messages)
        
        # 2. 全量压缩检测 (AI 总结)
        self.messages = await run_auto_compact(self.messages, self.client)
        
        # 3. 构造分层提示词
        system_p = self._build_layered_prompt(user_input)
        
        # 4. 执行推理循环 (省略工具调用逻辑，仅展示核心状态流)
        current_payload = [{"role": "system", "content": system_p}] + self.messages + [{"role": "user", "content": user_input}]
        response = await self.client.generate(current_payload)
        
        self.messages.append({"role": "user", "content": user_input})
        self.messages.append({"role": "assistant", "content": response})
        self.last_interaction = time.time()
        
        return response