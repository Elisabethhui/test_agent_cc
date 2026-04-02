import asyncio
from compact_system import run_full_compact
from olmx_client import model_call
import os
# ✅ 关键：导入全局唯一的 SESSION_MEMORY
from session_memory import SESSION_MEMORY
# 【本地文件读取工具】支持 py/txt/md/json
# ==========================
def read_local_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"文件不存在: {file_path}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "文件编码错误"

async def demo():
    print("🔥 多文件单例版 - 测试开始")

    file_path = "/Users/huguoqing/zzzhu/code/start-claude-code/src/services/mcp/MCPConnectionManager.tsx"   # 可以是 xxx.py / demo.txt / readme.md
    # 2. 读取文件
    file_content = read_local_file(file_path)

    print(f"✅ 读取文件成功，长度：{len(file_content)} 字符")

    # 构造真实长对话
    test_messages = [
        {"role": "user", "content": "分析这段代码：\n" + file_content, "id": "msg1"},
        {"role": "assistant", "content": "我来帮你分析 MCP 连接管理器", "id": "msg2"},
    ]

    # ✅ 设置全局记忆（整个系统唯一实例）
    SESSION_MEMORY.memory = f"""
文件：MCPConnectionManager.tsx
功能：管理 MCP 长连接、重连、状态管理、事件分发
用户需求：分析代码结构、优化点、bug风险
"""

    # ✅ 执行压缩系统
    result = await run_full_compact(test_messages, model_call)

    # 输出结果
    print("\n" + "="*80)
    print("✅ 压缩完成，最终上下文：")
    print("="*80)
    for idx, m in enumerate(result):
        print(f"{idx+1}. [{m['role']}] {m['content'][:120]}...")

if __name__ == "__main__":
    asyncio.run(demo())
