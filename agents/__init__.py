# agents/__init__.py
from .plan_agent import PLAN_AGENT
from .explore_agent import EXPLORE_AGENT
from .verification_agent import VERIFICATION_AGENT
from .general_agent import GENERAL_AGENT
from .guide_agent import GUIDE_AGENT
from .statusline_agent import STATUSLINE_AGENT

# 定义所有内置智能体的注册映射
AGENT_REGISTRY = {
    "Plan": PLAN_AGENT,
    "Explore": EXPLORE_AGENT,
    "verification": VERIFICATION_AGENT,
    "general-purpose": GENERAL_AGENT,
    "claude-code-guide": GUIDE_AGENT,
    "statusline-setup": STATUSLINE_AGENT
}

def get_agent_by_type(agent_type: str):
    """根据类型名称获取智能体定义，找不到则返回通用版"""
    return AGENT_REGISTRY.get(agent_type, GENERAL_AGENT)