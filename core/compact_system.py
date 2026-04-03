# core/compact_system.py
from typing import List, Callable, Awaitable, Any
from .micro_compact import micro_compact
from .session_memory import try_session_memory_compact, SESSION_MEMORY
from config import CONFIG
from utils import estimate_tokens

async def run_full_compact(
    messages: List[dict],
    model_call: Callable[[List[dict]], Awaitable[Any]]
) -> List[dict]:
    """
    核心：上下文压缩调度系统
    1. 物理清理 (Micro Compact)
    2. 逻辑折叠 (Session Memory Restore)
    3. AI 总结压缩 (Summarization with Sandwiching)
    """
    # 步骤 1: 清理旧的大型工具输出
    messages = micro_compact(messages)
    
    # 步骤 2: 尝试从全局单例记忆中恢复简洁上下文
    compacted = try_session_memory_compact(messages)
    if compacted:
        return compacted

    # 步骤 3: 检查 Token 水位，若超限则生成 AI 总结
    total_tokens = sum(estimate_tokens(m.get("content", "")) for m in messages)
    
    if total_tokens > CONFIG.MAX_RETAIN_TOKENS:
        print(f"⚠️ 上下文过载 ({total_tokens} tokens)，正在调用 AI 生成高精度总结...")
        
        to_summarize = messages[:-CONFIG.MIN_RETAIN_MESSAGES]
        keep_messages = messages[-CONFIG.MIN_RETAIN_MESSAGES:]
        
        # 采用“夹心饼干”提示词技术：首尾双重强调禁止调用工具
        summary_payload = [
            {"role": "system", "content": "【指令：开始】你是高精度对话总结器。禁止调用任何工具。仅输出纯文本事实摘要。"},
            {"role": "user", "content": f"请总结以下对话的关键技术事实：\n{to_summarize}"},
            {"role": "system", "content": "【指令：结尾】提醒：禁止输出 XML 标签或工具调用，仅输出文本。"}
        ]
        
        summary_result = await model_call(summary_payload)
        
        # 更新单例记忆，确保后续子智能体也能获得背景
        SESSION_MEMORY.memory = summary_result
        
        return [
            {"role": "user", "content": f"【历史对话压缩总结】\n{summary_result}"},
            *keep_messages
        ]
    
    return messages