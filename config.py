# config.py
from dataclasses import dataclass, field
from typing import Set

@dataclass
class CompactConfig:
    """全局配置，定义 Token 阈值和工具名称映射"""
    # 消息保留与压缩策略
    MIN_RETAIN_TOKENS: int = 4000      # 压缩后最少保留的 Token 数量
    MIN_RETAIN_MESSAGES: int = 5       # 压缩时最少保留的对话轮次
    MAX_RETAIN_TOKENS: int = 12000     # 触发 AI 总结压缩的阈值 (Token 数)
    
    # 逻辑阈值
    TIME_GAP_MINUTES: int = 30         # 触发微压缩的时间间隔
    KEEP_RECENT_TOOLS: int = 3         # 微压缩时保留的最新工具调用数量
    CLEARED_MESSAGE: str = "[为了优化上下文，该旧工具的详细执行结果已被清理]"
    
    # 系统工具名称映射 (映射自 TS 代码中的常量)
    BASH_TOOL = "bash"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_EDIT = "file_edit"
    GLOB_TOOL = "glob"
    GREP_TOOL = "grep"
    AGENT_TOOL = "agent"

CONFIG = CompactConfig()

# 定义在微压缩过程中允许直接清除内容的工具类型
CLEARABLE_TOOL_RESULTS: Set[str] = {
    CONFIG.FILE_READ, CONFIG.BASH_TOOL, CONFIG.GREP_TOOL, CONFIG.GLOB_TOOL
}