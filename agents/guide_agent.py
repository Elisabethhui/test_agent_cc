# agents/guide_agent.py
import json
from .base import AgentDefinition

def get_guide_prompt(context=None) -> str:
    """复刻 Guide 专家，动态感知环境配置"""
    base_prompt = "你是一位 Claude 向导专家。负责解释 Claude Code CLI、SDK 和 API 的使用方法。"
    
    if context and "active_mcp_servers" in context:
        mcp_info = "\n".join([f"- {s}" for s in context["active_mcp_servers"]])
        base_prompt += f"\n\n当前项目中配置的 MCP 服务器：\n{mcp_info}"
        
    return base_prompt

GUIDE_AGENT = AgentDefinition(
    agent_type="claude-code-guide",
    when_to_use="回答有关 Claude Code 功能、设置、MCP 或 SDK 的问题时使用。",
    get_system_prompt=get_guide_prompt
)