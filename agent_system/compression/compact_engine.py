from agent_system.core.config import CONFIG
from agent_system.core.utils import estimate_tokens
from agent_system.compression.grouping import group_by_api_round
from agent_system.compression.micro_compact import micro_compact
from agent_system.compression.post_clean import post_compact_cleanup
from agent_system.memory.agent_memory import AGENT_MEMORY

SUMMARY_PROMPT = """
你是高精度对话压缩器。输出：
1. 用户需求
2. 关键技术
3. 文件/代码
4. 错误与修复
5. 解决过程
6. 待办
7. 进度
8. 下一步
"""

# async def run_full_compact(messages, session_id: str, model_call, is_main_thread=True):
#     messages = micro_compact(messages)
#     memory = AGENT_MEMORY.get(session_id)

#     if memory.compressed_history:
#         new_msgs = [
#             {"role": "user", "content": f"【压缩记忆】\n{memory.compressed_history}"},
#             *messages[-CONFIG.MIN_RETAIN_MESSAGES:]
#         ]
#         post_compact_cleanup(session_id, is_main_thread)
#         return new_msgs

#     total = sum(estimate_tokens(m.get("content")) for m in messages)
#     if total < CONFIG.MAX_RETAIN_TOKENS:
#         return messages

#     groups = group_by_api_round(messages)
#     keep_msgs = [x for g in groups[-CONFIG.MIN_RETAIN_MESSAGES:] for x in g]
#     to_summarize = [x for g in groups[:-CONFIG.MIN_RETAIN_MESSAGES] for x in g]

#     summary = await model_call([
#         {"role": "system", "content": SUMMARY_PROMPT},
#         {"role": "user", "content": f"总结：{to_summarize}"}
#     ])

#     AGENT_MEMORY.update_compressed(session_id, summary)

#     new_msgs = [
#         {"role": "user", "content": f"【压缩记忆】\n{summary}"},
#         *keep_msgs
#     ]

#     post_compact_cleanup(session_id, is_main_thread)
#     return new_msgs
async def run_full_compact(messages, session_id: str, model_call, is_main_thread=True):
    messages = micro_compact(messages)
    memory = AGENT_MEMORY.get(session_id)

    total_tokens = sum(estimate_tokens(m.get("content", "")) for m in messages)
    print(f"📊 动态压缩检测 | 当前token：{total_tokens} / {CONFIG.MAX_RETAIN_TOKENS}")

    # 已有压缩记忆
    if memory.compressed_history:
        print("✅ 使用历史压缩记忆")
        new_msgs = [
            {"role": "user", "content": f"【上下文记忆】\n{memory.compressed_history}"},
            *messages[-CONFIG.MIN_RETAIN_MESSAGES:]
        ]
        post_compact_cleanup(session_id, is_main_thread)
        return new_msgs

    # 不触发压缩
    if total_tokens < CONFIG.MAX_RETAIN_TOKENS:
        print("✅ 未达到压缩阈值，不压缩")
        return messages

    # 触发压缩
    print("🔥 触发动态压缩，正在总结历史对话...")

    groups = group_by_api_round(messages)
    keep_count = CONFIG.MIN_RETAIN_MESSAGES

    # 👇 修复核心：保证不会出现空列表
    if len(groups) <= keep_count:
        keep_msgs = messages
        to_summarize = []
    else:
        keep_groups = groups[-keep_count:]
        to_summarize_groups = groups[:-keep_count]
        keep_msgs = [item for sublist in keep_groups for item in sublist]
        to_summarize = [item for sublist in to_summarize_groups for item in sublist]

    if not to_summarize:
        print("⚠️ 无历史消息可压缩")
        return messages

    summary = await model_call([
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": f"请总结以下代码和对话：\n{to_summarize}"}
    ])

    AGENT_MEMORY.update_compressed(session_id, summary)

    new_msgs = [
        {"role": "user", "content": f"【压缩总结】\n{summary}"},
        *keep_msgs
    ]

    post_compact_cleanup(session_id, is_main_thread)
    return new_msgs