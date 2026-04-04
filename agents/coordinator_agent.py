# agents/coordinator_agent.py
from agents.base import BaseAgent

class CoordinatorAgent(BaseAgent):
    """
    复刻 coordinatorMode.ts
    负责任务拆解与分发
    """
    def __init__(self):
        self.name = "Coordinator"
        self.system_prompt = """
你是 Claude Code 的协调中心。
你的职责：
1. 接收复杂任务并进行思维链拆解 (CoT)。
2. 决定是否需要分身 (Fork) 出 Plan、Explore 或 Verification 专家。
3. 协调多智能体之间的结果汇总。
=== CRITICAL ===
始终使用结构化的思维过程：[RESEARCH] -> [PLAN] -> [EXECUTE] -> [VERIFY]
"""
        self.agent_type = "coordinator"
