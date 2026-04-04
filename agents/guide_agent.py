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

GUIDE_AGENT0 = AgentDefinition(
    agent_type="claude-code-guide",
    when_to_use="回答有关 Claude Code 功能、设置、MCP 或 SDK 的问题时使用。",
    get_system_prompt=get_guide_prompt
)
# agents/guide_agent.py
from .base import BaseAgent
from config import CONFIG

GUIDE_AGENT = BaseAgent(
    name="GuideAgent",
    agent_type="guide",
    system_prompt="""你现在是 Claude Code 的助手向导 (Guide Agent)。
你的职责是帮助用户了解工具的使用方法、项目背景以及回答通用的编程问题。
你是一个友好的对话者，专注于提供信息而非直接修改代码。""",
    disallowed_tools=[CONFIG.FILE_WRITE, CONFIG.FILE_EDIT, CONFIG.BASH]
)