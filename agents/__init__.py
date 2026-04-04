# agents/__init__.py
from .base import BaseAgent
from .plan_agent import PLAN_AGENT
from .explore_agent import EXPLORE_AGENT
from .verification_agent import VERIFICATION_AGENT
from .general_agent import GENERAL_AGENT
from .guide_agent import GUIDE_AGENT
from .statusline_agent import STATUSLINE_AGENT

# 核心注册映射
AGENT_REGISTRY = {
    "Plan": PLAN_AGENT,
    "Explore": EXPLORE_AGENT,
    "verification": VERIFICATION_AGENT,
    "general-purpose": GENERAL_AGENT,
    "claude-code-guide": GUIDE_AGENT,
    "statusline-setup": STATUSLINE_AGENT
}

def get_agent_by_type(agent_type: str) -> BaseAgent:
    """根据名称从注册表中获取智能体，默认返回通用执行者"""
    return AGENT_REGISTRY.get(agent_type, GENERAL_AGENT)

# 注意：其他 Agent 文件的实现结构与 plan_agent.py 类似，此处省略重复的 Class 定义