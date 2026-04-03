# agents/general_agent.py
from .base import AgentDefinition

def get_general_prompt(context=None) -> str:
    """全能执行者 Prompt"""
    return "你是一个通用的代码开发专家。利用可用工具完整、高效地完成用户交付的开发、研究或修复任务。"

GENERAL_AGENT = AgentDefinition(
    agent_type="general-purpose",
    when_to_use="通用的研究和多步任务执行器。默认的智能体角色。",
    tools=["*"],
    get_system_prompt=get_general_prompt
)