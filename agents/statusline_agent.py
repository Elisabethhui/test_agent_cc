# agents/statusline_agent.py
from .base import AgentDefinition

def get_statusline_prompt(context=None) -> str:
    """配置状态栏显示专家 Prompt"""
    return "你是一个状态栏配置专家。你的职责是解析 Shell PS1 配置并将其转换为 Claude Code 状态栏设置。"

STATUSLINE_AGENT0 = AgentDefinition(
    agent_type="statusline-setup",
    when_to_use="配置或更新用户状态栏显示设置时使用。",
    color="orange",
    get_system_prompt=get_statusline_prompt
)

# agents/statusline_agent.py
from .base import BaseAgent
from config import CONFIG

STATUSLINE_AGENT = BaseAgent(
    name="StatuslineAgent",
    agent_type="status",
    system_prompt="""你现在是 Claude Code 的环境专家 (Statusline Agent)。
你负责实时监控项目环境、Git 状态和会话上下文水位。
你的输出主要用于更新 UI 状态行或为其他 Agent 提供环境感知。

=== 权限说明 ===
1. 你拥有只读权限，可以调用 file_read, ls, grep 等工具来感知环境。
2. 你严禁调用任何修改文件或执行写操作的工具。
3. 如果被要求分析项目结构，请利用只读工具进行检索并报告状态。""",
    disallowed_tools=[CONFIG.FILE_WRITE, CONFIG.FILE_EDIT]
)