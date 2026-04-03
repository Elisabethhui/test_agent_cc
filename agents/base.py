# agents/base.py
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Any

@dataclass
class AgentDefinition:
    """
    映射 TypeScript 中的 BuiltInAgentDefinition
    定义智能体的核心属性、提示词生成逻辑及工具限制
    """
    agent_type: str         # 智能体类型名称
    when_to_use: str        # 调度时机描述
    get_system_prompt: Callable[[Optional[dict]], str] # 系统提示词动态生成函数
    tools: List[str] = field(default_factory=lambda: ["*"]) # 允许使用的工具
    disallowed_tools: List[str] = field(default_factory=list) # 显式禁用的工具
    model: str = "inherit"  # 模型选择 (inherit, sonnet, haiku)
    color: Optional[str] = None # UI 显示颜色
    omit_claude_md: bool = False # 是否忽略 CLAUDE.md 上下文