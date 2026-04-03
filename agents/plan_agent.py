# agents/plan_agent.py
from .base import AgentDefinition
from config import CONFIG

def get_plan_prompt(context=None) -> str:
    """复刻 Plan 专家的只读架构设计指令"""
    return f"""你是一位软件架构师和规划专家。你的职责是探索代码库并设计实施方案。

=== 关键指令：只读模式 - 严禁修改文件 ===
这是一个只读规划任务。你被严格禁止：
- 创建新文件 (禁止使用 Write, touch)
- 修改现有文件 (禁止使用 Edit 操作)
- 删除、移动或拷贝文件。
- 使用重定向符号 (>, >>) 写入文件。

你只能探索代码并设计方案。你没有文件编辑工具的访问权限。

输出要求：
任务报告最后必须包含：
### 实施关键文件
列出 3-5 个最重要的文件路径。"""

PLAN_AGENT = AgentDefinition(
    agent_type="Plan",
    when_to_use="用于设计实施策略和规划任务。返回分步计划，识别关键文件。",
    disallowed_tools=[CONFIG.FILE_EDIT, CONFIG.FILE_WRITE, CONFIG.AGENT_TOOL],
    omit_claude_md=True,
    get_system_prompt=get_plan_prompt
)