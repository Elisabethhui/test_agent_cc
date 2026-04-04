# agents/general_agent.py
from .base import AgentDefinition

def get_general_prompt(context=None) -> str:
    """全能执行者 Prompt"""
    return "你是一个通用的代码开发专家。利用可用工具完整、高效地完成用户交付的开发、研究或修复任务。"

GENERAL_AGENT0 = AgentDefinition(
    agent_type="general-purpose",
    when_to_use="通用的研究和多步任务执行器。默认的智能体角色。",
    tools=["*"],
    get_system_prompt=get_general_prompt
)

# agents/general_agent.py
from .base import BaseAgent
from config import CONFIG

GENERAL_AGENT = BaseAgent(
    name="GeneralAgent",
    agent_type="general",
    system_prompt="""你现在是 Claude Code 的通用执行者 (General Agent)。
你是任务的主要实施者，拥有全量的工具调用权限。
你的目标是高效、准确地完成用户提出的代码改写、重构或新功能开发任务。""",
    # 通用执行者通常拥有所有权限
    disallowed_tools=[]
)

