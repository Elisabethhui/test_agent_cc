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



@dataclass
class BaseAgent:
    """
    统一的智能体定义类。
    注意：属性名必须是 system_prompt，以适配 executor.py
    """
    name: str
    agent_type: str
    system_prompt: str  # 确保这是一个属性
    disallowed_tools: List[str] = field(default_factory=list)
    fork_directive: Optional[str] = None

    # 为了兼容你报错中提到的 get_system_prompt，我们加一个 alias
    def get_system_prompt(self) -> str:
        return self.system_prompt