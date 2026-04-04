# config.py
from dataclasses import dataclass, field
from typing import Set

@dataclass
class CompactConfig:
    """全局配置，定义 Token 阈值、时间窗口和工具映射"""
    # 消息治理策略
    MIN_RETAIN_TOKENS: int = 4000      # 压缩后至少保留的 Token 
    MIN_RETAIN_MESSAGES: int = 5       # 压缩时保留的最近消息轮次
    MAX_RETAIN_TOKENS: int = 12000     # 触发 AI 总结的硬阈值 (测试时可调低)
    
    # 时间与物理清理
    TIME_GAP_THRESHOLD_MINS: int = 30  # 超过 30 分钟停顿触发微压缩
    KEEP_RECENT_TOOLS_COUNT: int = 2   # 物理清理时保留的最新工具结果数
    CLEARED_STUB: str = "[内容已物理剔除以节省上下文空间]"
    
    # 作用域路径模拟
    USER_MEM_DIR: str = "~/.claude/agent-memory/"
    PROJ_MEM_DIR: str = ".claude/agent-memory/"
    LOCAL_MEM_DIR: str = ".claude/agent-memory-local/"

    # 工具名定义
    BASH = "bash"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_EDIT = "file_edit"
    GREP = "grep"
    GLOB = "glob"

    # 系统工具名称映射 (映射自 TS 代码中的常量)
    BASH_TOOL = "bash"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_EDIT = "file_edit"
    GLOB_TOOL = "glob"
    GREP_TOOL = "grep"
    AGENT_TOOL = "agent"


CONFIG = CompactConfig()

# 允许物理剔除内容的工具列表
CLEARABLE_TOOLS = {CONFIG.BASH, CONFIG.FILE_READ, CONFIG.GREP, CONFIG.GLOB}

