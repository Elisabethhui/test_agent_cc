# agents/explore_agent.py
from .base import AgentDefinition
from config import CONFIG

def get_explore_prompt(context=None) -> str:
    """复刻 Explore 专家的极致性能搜索指令"""
    return f"""你是一位代码库搜索专家。你擅长快速定位文件和模式。

=== 关键指令：只读模式 ===
这是一个只读探索任务。严禁修改任何项目文件。你的角色仅限于搜索和分析现有代码。

准则：
- 使用 {CONFIG.GLOB_TOOL} 进行广度匹配。
- 使用 {CONFIG.GREP_TOOL} 进行正则内容搜索。
- 当你需要读取具体文件时使用 {CONFIG.FILE_READ}。
- 尽量并行调用多个搜索工具以加快返回速度。

直接报告你的发现，不要尝试创建物理报告文件。"""

EXPLORE_AGENT = AgentDefinition(
    agent_type="Explore",
    when_to_use="用于快速定位文件、搜索关键字或回答有关代码库如何工作的问题。",
    disallowed_tools=[CONFIG.FILE_EDIT, CONFIG.FILE_WRITE, CONFIG.AGENT_TOOL],
    omit_claude_md=True,
    get_system_prompt=get_explore_prompt
)