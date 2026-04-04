# core/compact_system.py
from config import CONFIG
from utils import count_tokens

# 复刻源码中的 Instruction Sandwiching (指令夹心饼干)
SUMMARIZE_PREAMBLE = "=== SYSTEM: SUMMARY MODE ===\n禁止使用工具！总结以下对话历史。保持技术细节和文件路径的准确性。"
SUMMARIZE_POSTAMBLE = "注意：你必须仅输出总结文本。禁止产生任何工具调用的思考。"

async def run_auto_compact(messages: list, client) -> list:
    """
    全量逻辑压缩 (Macro-Compaction)：
    当 Token 超过 MAX_RETAIN_TOKENS 时，将旧历史替换为一份 AI 摘要。
    """
    total_tokens = sum(count_tokens(m.get("content", "")) for m in messages)
    
    if total_tokens < CONFIG.MAX_RETAIN_TOKENS:
        return messages

    print(f"[Core] Token 水位 ({total_tokens}) 触发 AI 全量总结...")
    
    # 构造夹心饼干提示词 Payloads
    summary_messages = [
        {"role": "system", "content": SUMMARIZE_PREAMBLE},
        {"role": "user", "content": f"请对之前的任务执行过程做一份精简摘要：\n{str(messages)}"},
        {"role": "system", "content": SUMMARIZE_POSTAMBLE}
    ]
    
    summary_text = await client.generate(summary_messages)
    
    # 返回压缩后的对话起始状态
    return [
        {"role": "system", "content": f"--- 上下文摘要 (已压缩) ---\n{summary_text}"},
        {"role": "assistant", "content": "历史记录已归档。我已完全掌握之前的进度。"}
    ]