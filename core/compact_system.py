# core/compact_system.py
from config import MAX_CONTEXT_TOKENS
from utils import count_tokens

# 源码中的 NO_TOOLS_PREAMBLE 策略
SUMMARIZE_PREAMBLE = "=== CRITICAL: NO TOOLS ALLOWED ===\n你现在的任务是总结对话历史。禁止调用任何工具！"
SUMMARIZE_POSTAMBLE = "请注意：你必须仅输出总结文本，禁止尝试执行代码或读取文件。总结必须包含之前的关键决策和待办事项。"

async def run_auto_compact(messages: list, client) -> list:
    """
    全量总结逻辑 (复刻 compact.ts):
    利用 '指令夹心饼干' 强制模型生成纯文本摘要。
    """
    total_tokens = sum(count_tokens(str(m)) for m in messages)
    
    if total_tokens < MAX_CONTEXT_TOKENS:
        return messages

    print("⚠️ Context overflow! Running AI compaction...")
    
    # 构造夹心饼干 Payload
    summary_prompt = [
        {"role": "system", "content": SUMMARIZE_PREAMBLE},
        {"role": "user", "content": f"请总结以下对话历史：\n{str(messages)}"},
        {"role": "system", "content": SUMMARIZE_POSTAMBLE}
    ]
    
    summary_text = await client.generate(summary_prompt)
    
    # 替换旧历史
    new_history = [
        {"role": "system", "content": f"=== CONTEXT SUMMARY (Compacted) ===\n{summary_text}"},
        {"role": "assistant", "content": "历史记录已压缩。我已记住之前的关键结论。"}
    ]
    return new_history