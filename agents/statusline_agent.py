# agents/statusline_agent.py
from .base import AgentDefinition

def get_statusline_prompt(context=None) -> str:
    """配置状态栏显示专家 Prompt"""
    return "你是一个状态栏配置专家。你的职责是解析 Shell PS1 配置并将其转换为 Claude Code 状态栏设置。"

STATUSLINE_AGENT = AgentDefinition(
    agent_type="statusline-setup",
    when_to_use="配置或更新用户状态栏显示设置时使用。",
    color="orange",
    get_system_prompt=get_statusline_prompt
)