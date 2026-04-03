import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__)))

from agent_system import (
    run_full_compact,
    AGENT_MEMORY,
    AGENT_CONTEXT,
    AGENT_COORD,
    AgentType
)
from agent_system.mlx_client import model_call

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "文件读取失败"

async def demo():
    session_id = "proj_001"
    ctx = AGENT_CONTEXT.create(session_id)

    file_content = read_file("/Users/huguoqing/zzzhu/code/start-claude-code/src/tools/AgentTool/AgentTool.tsx")
    messages = [
        {"role": "user", "content": "分析代码\n" + file_content},
        {"role": "assistant", "content": "好的"}
    ]

    AGENT_MEMORY.get(session_id).task = "分析 MCP 连接管理器"

    compacted = await run_full_compact(
        messages,
        session_id,
        model_call,
        ctx.is_main_thread
    )

    print("✅ 压缩完成：")
    for m in compacted:
        print(f"{m['role']}: {m['content'][:80]}...")

    results = await AGENT_COORD.run_sequential(
        session_id,
        [AgentType.PLANNER, AgentType.CODE, AgentType.REVIEW],
        "完成代码分析与优化",
        model_call
    )

    print("\n🤖 多Agent 完成：")
    for typ, res in results:
        print(f"{typ}: {res}...")

if __name__ == "__main__":
    asyncio.run(demo())